import datetime as dt
import logging
from logging.config import dictConfig
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


DATE_STRING_FORMAT = '%Y-%m-%d'
DATETIME_STRING_FORMAT = '%Y-%m-%d_%H-%M-%S'


def datetime_to_string(datetime: dt.datetime) -> str:
    return datetime.strftime(DATETIME_STRING_FORMAT)


def string_to_datetime(string_datetime: str) -> dt.datetime:
    if len(string_datetime) == 10:
        return dt.datetime.strptime(string_datetime, DATE_STRING_FORMAT)
    else:
        return dt.datetime.strptime(string_datetime, DATETIME_STRING_FORMAT)


def timestamp_to_datetime_utc(timestamp: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)


def get_db_connection_string() -> str:
    type_ = os.environ.get('DB_TYPE', 'sqlite')
    host = os.environ.get('DB_HOST', '')
    port = os.environ.get('DB_PORT', '')
    name = os.environ.get('DB_NAME', 'test.db')
    user = os.environ.get('DB_USER', '')
    password = os.environ.get('DB_PASSWORD', '')

    if type_ != 'sqlite':
        s = f'{type_}://{user}:{password}@{host}:{port}/{name}'
    else:
        s = f'{type_}:///{name}'
    return s


def set_env(dotenv_config: Optional[str] = '') -> None:
    if dotenv_config:
        dotenv_config = Path(dotenv_config).absolute()
        logger.info(f'Loading environment config {dotenv_config}')
        if not dotenv_config.exists():
            raise FileExistsError(f'Cannot open config {dotenv_config}')
        else:
            load_dotenv(dotenv_path=dotenv_config)
    else:
        logger.warning('Config is not provided. Read from existing envs')


def set_logger_settings(log_file: Path, level: Optional[int] = logging.INFO) -> None:
    if not log_file.parent.exists():
        log_file.parent.mkdir(exist_ok=True, parents=True)

    logger_config = dict(
        version=1,
        formatters={'common': {'format': '%(asctime)s %(levelname)-8s [%(name)-8s] %(message)s'}},
        handlers={
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'common',
            },
            'api_request': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': level,
                'formatter': 'common',
                'filename': log_file,
                'mode': 'a',
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 5,
            },
        },
        loggers={
            'api_request': {'handlers': ['console', 'api_request'], 'level': level, 'propagate': False},
        },
        root={
            'handlers': ['console'],
            'level': level,
        },
        disable_existing_loggers=False,
    )
    dictConfig(logger_config)
