"""
Extension of sanic.server.HttpProtocol to extend access_log functionality
"""
from sanic.server import HttpProtocol
from sanic.response import HTTPResponse


class ONSHttpProtocol(HttpProtocol):

    def log_response(self, response):
        """
        Extends the log_response method from sanic.server.HttpProtocol to include additional request info
        :param response:
        :return:
        """
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
                if self.request.ip:
                    extra['host'] = '{0}:{1}'.format(self.request.ip,
                                                     self.request.port)

                extra['request'] = '{0} {1}'.format(self.request.method,
                                                    self.request.url)
            else:
                extra['request'] = 'nil'

            access_logger.info('', extra=extra)