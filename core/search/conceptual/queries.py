from elasticsearch_dsl import query as Q


class ScriptScore(Q.Query):
    name = "script_score"


class FunctionScore(Q.Query):
    name = "function_score"


class RescoreQuery(Q.Query):
    name = "rescore"
