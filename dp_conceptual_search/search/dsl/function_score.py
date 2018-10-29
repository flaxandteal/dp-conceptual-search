from elasticsearch_dsl import query as Q


class FunctionScore(Q.Query):
    name = "function_score"
