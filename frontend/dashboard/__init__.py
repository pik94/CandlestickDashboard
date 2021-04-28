import datetime as dt
import logging
import os
from pathlib import Path
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from flask import Flask

from dashboard.candlesticks import CandlestickApp
from dashboard.utils import DateTimeHelper, set_env, set_logger_settings


def create_app(config: Optional[str] = '', debug: Optional[bool] = False) -> CandlestickApp:
    set_env(config)
    level = logging.DEBUG if debug else logging.INFO

    now = DateTimeHelper.datetime_to_string(dt.datetime.utcnow())
    log_name = f'candlestick_dashboard_{os.getpid()}_{now}.log'
    set_logger_settings(Path(os.environ['LOG_DIR']) / log_name, level)
    os.environ['LOG'] = log_name

    server = Flask(__name__)
    app = dash.Dash('dash_app', server, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP])

    candlestick_app = CandlestickApp(app)

    return candlestick_app
