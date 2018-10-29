"""
Custom ONS HttpProtocol to override logging behaviour
"""
from sanic.log import access_logger
from sanic.server import HttpProtocol
from sanic.response import HTTPResponse

from dp_conceptual_search.api.request.ons_request import ONSRequest


class ONSHttpProtocol(HttpProtocol):
    def log_response(self, response):
        if self.access_log:
            extra = {
                'status': getattr(response, 'status', 0),
            }

            if isinstance(response, HTTPResponse):
                extra['byte'] = len(response.body)
            else:
                extra['byte'] = -1

            extra['host'] = 'UNKNOWN'
            if self.request is not None:
                if isinstance(self.request, ONSRequest):
                    # Add request ID to logs
                    extra["context"] = self.request.request_id
                if self.request.ip:
                    extra['host'] = '{0}:{1}'.format(self.request.ip,
                                                     self.request.port)

                extra['method'] = self.request.method
                extra['path'] = self.request.path
                extra['query'] = self.request.query_string
            else:
                extra['request'] = 'nil'

            access_logger.info('received request', extra=extra)
