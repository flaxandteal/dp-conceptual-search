"""
Defines useful query objects
"""
from elasticsearch_dsl import query as Q


class RescoreQuery(Q.Query):
    name = "rescore"


class ScriptScore(Q.Query):
    name = "script_score"
