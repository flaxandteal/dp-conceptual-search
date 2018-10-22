"""
Useful class for building decay functions based on date fields
"""
from elasticsearch_dsl import query as Q


class DateDecayFunction(Q.SF):
    def __init__(self, field: str, fn: str, scale: str, offset: str, decay: float, origin: str="now"):
        super(DateDecayFunction, self).__init__(
            fn, **{
                field: {
                    "origin": origin,
                    "scale": scale,
                    "offset": offset,
                    "decay": decay
                }
            }
        )
