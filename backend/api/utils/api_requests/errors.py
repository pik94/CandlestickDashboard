import traceback

from flask import session

from api.database import db
from api.utils.api_requests.loggers import ApiRequestLogger


def handle_database_error(e):
    request_id = session['request_id']
    logger = ApiRequestLogger.get_logger(request_id)
    db.session.rollback()
    logger.info('Rollback changes...')
    logger.error(traceback.format_exc())

    return 'Bad request', 500


def handle_error(e):
    request_id = session['request_id']
    logger = ApiRequestLogger.get_logger(request_id)
    logger.info('Process common error')
    logger.error(traceback.format_exc())

    return 'Bad request', 500
