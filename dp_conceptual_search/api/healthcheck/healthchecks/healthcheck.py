"""
Abstract class for health checks
"""
import abc
from typing import Tuple

from dp_conceptual_search.api.request import ONSRequest


class HealthCheck(abc.ABC):

    @abc.abstractmethod
    async def healthcheck(self, request: ONSRequest) -> Tuple[str, int]:
        pass
