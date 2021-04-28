import datetime as dt
import os
import uuid

from flask import Response, request, session
from sqlalchemy.exc import SQLAlchemyError

from api.database import db, ApiRequestMetadata
from api.utils.misc.helpers import string_to_datetime, datetime_to_string
from api.utils.api_requests.loggers import ApiRequestLogger


def init_request_metadata():
    request_id = uuid.uuid4().hex
    if 'request_id' in session:
        session.pop('request_id')

    session['request_id'] = request_id
    start_at = dt.datetime.utcnow()
    session['request_start_at'] = datetime_to_string(start_at)
    log_name = os.environ['LOG']
    request_metadata = ApiRequestMetadata(
        request_id=request_id, start_at=start_at, log_file=log_name, method=request.method, base_url=request.base_url
    )
    db.session.add(request_metadata)
    db.session.commit()


def update_request_metadata(response: Response):
    request_id = session['request_id']
    start_at = string_to_datetime(session['request_start_at'])
    request_metadata = db.session.query(ApiRequestMetadata).filter(ApiRequestMetadata.request_id == request_id).first()

    end_at = dt.datetime.utcnow()
    duration = (end_at - start_at).total_seconds()
    status = response.status_code
    request_metadata.end_at = end_at
    request_metadata.duration = duration
    request_metadata.status = status

    try:
        db.session.add(request_metadata)
        db.session.commit()
    except SQLAlchemyError:
        logger = ApiRequestLogger.get_logger(request_id)
        db.session.rollback()
        logger.error('Cannot upload request metadata')

    session.pop('request_id')
    session.pop('request_start_at')
    return response
