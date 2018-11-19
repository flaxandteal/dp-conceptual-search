"""
Define an enum of all services to health check
"""
from .healthchecks import check_elasticsearch_health

from enum import Enum
from functools import partial


class Service(Enum):
    elasticsearch = partial(check_elasticsearch_health)
