"""
Enum of available ONS indexes
"""
from enum import Enum

from dp_conceptual_search.config import CONFIG


class Index(Enum):
    ONS = CONFIG.SEARCH.search_index
    DEPARTMENTS = CONFIG.SEARCH.departments_search_index
