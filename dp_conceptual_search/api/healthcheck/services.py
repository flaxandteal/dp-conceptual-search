"""
Define an enum of all services to health check
"""
from .healthchecks.healthcheck import HealthCheck

from .healthchecks import ElasticsearchHealthCheck, DpFastTextHealthCheck

from enum import Enum


class Service(Enum):
    elasticsearch: HealthCheck = ElasticsearchHealthCheck()
    dp_fasttext: HealthCheck = DpFastTextHealthCheck()
