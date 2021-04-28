from api.database.database import db


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(db.String, nullable=True, default=True)
    isin = db.Column(db.String, nullable=True, default=True)
    currency = db.Column(db.String, nullable=True, default='USD')

    candlesticks = db.relationship('Candlestick', back_populates='asset')

    def __repr__(self) -> str:
        return f'Asset(isin={self.isin}, currency={self.currency}, ticker={self.ticker})'

    __str__ = __repr__


class Candlestick(db.Model):
    __tablename__ = 'candlesticks'
    __table_args__ = (db.UniqueConstraint('datetime', 'asset_id', name='unique_candlesticks_date_asset_id'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False)
    low_price = db.Column(db.Float, nullable=True, default=None)
    high_price = db.Column(db.Float, nullable=True, default=None)
    open_price = db.Column(db.Float, nullable=True, default=None)
    close_price = db.Column(db.Float, nullable=True, default=None)
    volume = db.Column(db.Float, nullable=True)
    weighted_volume = db.Column(db.Float, nullable=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))

    asset = db.relationship('Asset', back_populates='candlesticks', uselist=False)

    def __repr__(self) -> str:
        return (
            f'Candlestick(datetime={self.datetime}, close_price={self.close_price}, open_price={self.open_price}, '
            f'low_price={self.low_price}, high_price={self.high_price}), volume={self.volume}'
        )

    __str__ = __repr__


class ApiRequestMetadata(db.Model):
    __tablename__ = 'api_request_metadata'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(length=32))
    start_at = db.Column(db.DateTime, nullable=True, default=None)
    end_at = db.Column(db.DateTime, nullable=True, default=None)
    duration = db.Column(db.Float, nullable=True, default=None)
    method = db.Column(db.String(5), nullable=True, default=None)
    base_url = db.Column(db.String)
    log_file = db.Column(db.String, nullable=True, default=None)
    status = db.Column(db.SmallInteger, nullable=True, default=None)
