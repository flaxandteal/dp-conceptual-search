from enum import Enum


class Endpoint(Enum):
    CONTENT = 'content'
    TYPE_COUNTS = 'counts'
    FEATURED = 'featured'
    DEPARTMENTS = 'departments'


available_endpoints = [e.value for e in Endpoint]
