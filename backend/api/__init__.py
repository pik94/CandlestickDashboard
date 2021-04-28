import datetime as dt
import logging
import os
from pathlib import Path
from typing import Optional

from flask import Flask
from flask_migrate import Migrate

from api.utils.misc.helpers import DATETIME_STRING_FORMAT, get_db_connection_string, set_env, set_logger_settings


def create_app(config: Optional[str] = '', debug: Optional[bool] = False) -> Flask:
    set_env(config)
    level = logging.DEBUG if debug else logging.INFO

    now = dt.datetime.utcnow().strftime(DATETIME_STRING_FORMAT)
    log_name = f'api_{os.getpid()}_{now}.log'
    set_logger_settings(Path(os.environ['LOG_DIR']) / log_name, level)
    os.environ['LOG'] = log_name

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_connection_string()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ['CRLF_TOKEN']

    add_extensions(app)
    add_blueprints(app)

    return app


def add_extensions(app: Flask) -> None:
    from api.database import db

    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)


def add_blueprints(app: Flask) -> None:
    from api.endpoints import asset_blueprint

    app.register_blueprint(asset_blueprint)
