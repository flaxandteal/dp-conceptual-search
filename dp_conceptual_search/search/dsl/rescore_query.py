"""
Defines the DSL for a rescore query
"""
from elasticsearch_dsl import query as Q


class RescoreQuery(Q.Query):
    name = "rescore"