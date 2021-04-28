import datetime as dt
import logging
from logging.config import dictConfig
from pathlib import Path
from typing import Optional
import uuid

from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class DateTimeHelper:
    DATE_STRING_FORMAT = '%Y-%m-%d'
    DATETIME_STRING_FORMAT = '%Y-%m-%d_%H-%M-%S'

    @classmethod
    def datetime_to_string(cls, datetime: dt.datetime) -> str:
        return datetime.strftime(cls.DATETIME_STRING_FORMAT)

    @classmethod
    def date_to_string(cls, date: dt.date) -> str:
        return date.strftime(cls.DATE_STRING_FORMAT)

    @classmethod
    def string_to_datetime(cls, string_datetime: str) -> dt.datetime:
        return dt.datetime.strptime(string_datetime, cls.DATETIME_STRING_FORMAT)

    @classmethod
    def string_to_date(cls, string_date: str) -> dt.date:
        return dt.datetime.strptime(string_date, cls.DATE_STRING_FORMAT).date()

    @classmethod
    def timestamp_to_datetime_utc(cls, timestamp: int) -> dt.datetime:
        return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)

    @classmethod
    def date_to_datetime(cls, date: dt.date) -> dt.datetime:
        return dt.datetime(date.year, date.month, date.day)


def generate_id() -> str:
    return uuid.uuid4().hex


def set_logger_settings(log_file: Path, level: Optional[int] = logging.INFO) -> None:
    if not log_file.parent.exists():
        log_file.parent.mkdir(exist_ok=True, parents=True)

    logger_config = dict(
        version=1,
        formatters={'common': {'format': '%(asctime)s %(levelname)-8s ' '[%(name)-8s] %(message)s'}},
        handlers={
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'common',
            },
            'file': {
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
            'file': {'handlers': ['console', 'file'], 'level': level, 'propagate': False},
        },
        root={
            'handlers': ['console', 'file'],
            'level': level,
        },
        disable_existing_loggers=False,
    )
    dictConfig(logger_config)


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
