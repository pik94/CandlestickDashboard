from marshmallow import Schema, fields, post_load

from api.database.models import Candlestick
from api.utils.misc.helpers import DATETIME_STRING_FORMAT


class AssetSchema(Schema):
    id = fields.Integer()
    ticker = fields.String()
    isin = fields.String()
    currency = fields.String()

    candlesticks = fields.Nested('CandlestickSchema', many=True)


class CandlestickSchema(Schema):
    id = fields.Integer()
    datetime = fields.DateTime(format=DATETIME_STRING_FORMAT)
    low_price = fields.Float()
    high_price = fields.Float()
    open_price = fields.Float()
    close_price = fields.Float()
    volume = fields.Float()
    weighted_volume = fields.Float()

    @post_load
    def make_load(self, data, **kwargs) -> Candlestick:
        return Candlestick(**data)
