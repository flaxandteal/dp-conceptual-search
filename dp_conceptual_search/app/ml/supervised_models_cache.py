"""
Cache for supervised ML models
"""
import logging

from dp_conceptual_search.ml.word_embedding.fastText.supervised import SupervisedModel


_cache = {}


def get_supervised_model(fname):
    """
    Initialise the supervised fastText .bin model
    :return:
    """
    if fname not in _cache:
        logging.info("Initialising supervised fastText model", extra={
            "model": {
                "filename": fname
            }
        })

        _cache[fname] = SupervisedModel(fname)

        logging.info("Successfully initialised supervised fastText model", extra={
            "model": {
                "filename": fname
            }
        })
    return _cache[fname]
