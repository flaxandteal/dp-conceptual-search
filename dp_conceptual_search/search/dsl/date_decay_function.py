"""
Useful class for building decay functions based on date fields
"""
from elasticsearch_dsl import query as Q


def date_decay_function(field: str, fn: str, scale: str, offset: str, decay: float, origin: str="now"):
    """
    Builds a decay function useful for boosting more recent content
    :param field:
    :param fn:
    :param scale:
    :param offset:
    :param decay:
    :param origin:
    :return:
    """
    return Q.SF(
        fn, **{
            field: {
                "origin": origin,
                "scale": scale,
                "offset": offset,
                "decay": decay
            }
        }
    )
