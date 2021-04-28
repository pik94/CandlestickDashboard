import datetime as dt
from typing import Dict, List, Union

from flask import jsonify, request, session
from flask.views import MethodView
from sqlalchemy import and_, or_

from api.database import db, Asset, Candlestick
from api.schemas import CandlestickSchema
from api.utils.misc.helpers import datetime_to_string, string_to_datetime
from api.utils.api_requests.loggers import ApiRequestLogger


CandlestickData = Dict[str, Union[str, Dict[str, float]]]


class AssetView(MethodView):
    methods = ['GET', 'POST']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request_id = session['request_id']
        self.logger = ApiRequestLogger.get_logger(request_id)

    def get(self, field: str, ticker: str, from_: str, to: str):
        asset = db.session.query(Asset).filter(Asset.ticker == ticker).first()
        if not asset:
            self.logger.warning(f'Cannot find an asset for ticker {ticker}')
            return jsonify({})

        data = {
            'ticker': ticker,
            'status': 'OK',
            'results': {},
        }

        from_ = string_to_datetime(from_)
        to = string_to_datetime(to) + dt.timedelta(hours=23, minutes=59, seconds=59)
        if from_ > to:
            return data, 200

        if field == 'candlesticks':
            self.logger.debug('Get candlestick data...')
            data['results'] = self._get_candlestick_data(asset, from_, to)
        else:
            self.logger.warning(f'Cannot prepare data for "{field}". Unknown field')
        return data, 200

    def _get_candlestick_data(self, asset: Asset, from_: dt.date, to: dt.date) -> CandlestickData:
        self.logger.debug(
            f'Request to db for candlesticks for asset={asset.id} ({asset.ticker}), ' f'from={from_}, to={to}'
        )
        candlesticks = (
            db.session.query(Candlestick)
            .filter(
                and_(
                    Candlestick.asset_id == asset.id,
                    Candlestick.datetime.between(from_, to),
                )
            )
            .order_by(Candlestick.datetime)
            .all()
        )
        candlestick_data = {}
        if candlesticks:
            self.logger.debug('Got candlestick data from db')
            candlestick_schema = CandlestickSchema()

            candlestick_data['data'] = candlestick_schema.dump(candlesticks, many=True)
            candlestick_data['min_datetime'] = datetime_to_string(candlesticks[0].datetime)
            candlestick_data['max_datetime'] = datetime_to_string(candlesticks[-1].datetime)
            candlestick_data['result_count'] = len(list(candlesticks))
        else:
            self.logger.debug('No candlestick data')

        return candlestick_data

    def post(self):
        json_data = request.json
        ticker = json_data.get('ticker')
        if not ticker:
            raise KeyError('Cannot extract asset info from the given data. No "ticker" key')

        asset = self._get_asset(ticker)

        if 'candlesticks' in json_data:
            self.logger.debug('Handle candlestick data')
            self._process_candlesticks(json_data['candlesticks'], asset)

        if db.session.new:
            self.logger.info('Upload new data')
            db.session.commit()

        return 'Created!', 200

    def _get_asset(self, ticker: str) -> Asset:
        asset = Asset.query.filter_by(ticker=ticker).first()
        if not asset:
            asset = Asset(ticker=ticker)
            db.session.add(asset)
        return asset

    def _process_candlesticks(self, candlestick_data: List[Dict[str, float]], asset: Asset) -> None:
        candlestick_schema = CandlestickSchema()
        candlesticks = candlestick_schema.load(candlestick_data, many=True)
        if asset.id:
            self.logger.debug(
                f'Request to db to get candlestick data for asset={asset.id} ({asset.ticker}) and '
                f'for the given datetime data'
            )
            ands = [
                Candlestick.asset_id == asset.id,
                Candlestick.datetime.in_([candlestick.datetime for candlestick in candlesticks]),
            ]

            db_candlesticks = db.session.query(Candlestick).filter(*ands).all()

            db_candlesticks = {(candlestick.datetime, asset.id): candlestick for candlestick in db_candlesticks}
            self.logger.debug(f'Got {len(db_candlesticks)} candlestick rows from db')

            for candlestick in candlesticks:
                key = (candlestick.datetime, asset.id)
                db_candlestick = db_candlesticks.get(key)
                if not db_candlestick:
                    candlestick.asset_id = asset.id
                    db.session.add(candlestick)
                    self.logger.debug(f'Put to db a new candlestick: {candlestick}')
                else:
                    self.logger.debug(f'Candlestick is already in db: {candlestick}')

        else:
            asset.candlesticks.extend(candlesticks)
