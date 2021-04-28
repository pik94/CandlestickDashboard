from api.endpoints.assets.views import AssetView

from flask import Blueprint
from api.utils.api_requests import handle_database_error, handle_error, init_request_metadata, update_request_metadata
from sqlalchemy.exc import SQLAlchemyError


asset_view = AssetView.as_view('asset_view')

asset_blueprint = Blueprint('asset_blueprint', __name__, url_prefix='/')
asset_blueprint.before_request(init_request_metadata)
asset_blueprint.after_request(update_request_metadata)
asset_blueprint.register_error_handler(SQLAlchemyError, handle_database_error)
asset_blueprint.register_error_handler(Exception, handle_error)
asset_blueprint.add_url_rule('/assets', view_func=asset_view)
asset_blueprint.add_url_rule('/assets/<string:field>/<string:ticker>/<string:from_>/<string:to>', view_func=asset_view)
