"""
Defines the DSL for a script score
"""
from elasticsearch_dsl import query as Q


class ScriptScore(Q.Query):
    name = "script_score"
