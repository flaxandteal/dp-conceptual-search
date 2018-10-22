"""
Useful class for building decay functions based on date fields
"""
from elasticsearch_dsl import query as Q


class DateDecayFunction(Q.SF):
    def __init__(self):
        pass