"""
Define class for HealthCheck responses
"""
from .services import Service


class HealthCheckResponse(object):

    def __init__(self):
        self._service_status = {}

        self.is_healthy = True

    def set_response_for_service(self, service: Service, response: str, code: int):
        self._service_status[service.name] = response
        if self.is_healthy and code == 500:
            self.is_healthy = False

    def to_dict(self) -> dict:
        return self._service_status
