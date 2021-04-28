import logging
from typing import Optional
import uuid


API_REQUEST_LOGGER_NAME = 'api_request'


class ApiRequestLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        request_id = kwargs.get('request_id', self.extra['request_id'])
        return f'Request ID={request_id} - {msg}', kwargs

    @classmethod
    def get_logger(
        cls, request_id: Optional[str] = uuid.uuid4().hex, name: Optional[str] = API_REQUEST_LOGGER_NAME
    ) -> 'ApiRequestLogger':
        """
        Create a new logger for the given request ID.
        """

        return cls(logging.getLogger(name), {'request_id': request_id})
