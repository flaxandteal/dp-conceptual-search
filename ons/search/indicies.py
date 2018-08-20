import os
from enum import Enum


class Index(Enum):
    ONS = os.environ.get('SEARCH_INDEX', 'ons')
    DEPARTMENTS = 'departments'
