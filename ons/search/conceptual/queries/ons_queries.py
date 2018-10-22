"""
This file contains queries for conceptual search
"""
from elasticsearch_dsl import query as Q

from ons.search.fields import AvailableFields, Field
from ons.search.conceptual.exceptions import MalformedSearchTerm

from ml.word_embedding.fastText.supervised import SupervisedModel
from ml.word_embedding.utils import clean_string, replace_nouns_with_singulars


def word_vector_keywords_query(search_term: str, num_labels: int, threshold: float, model: SupervisedModel) -> Q.Query:
    """
    Build a bool query to match against generated keyword labels
    :param search_term:
    :param num_labels:
    :param threshold:
    :param model:
    :return:
    """
    # Use the raw keywords field for matching
    field: Field = AvailableFields.KEYWORDS_RAW.value

    # Get predicted labels and their probabilities
    labels, probabilities = model.predict(search_term, k=num_labels, threshold=threshold)

    # Build the individual match queries
    match_queries = [Q.Match(**{field.name: {"query": label}}) for label in labels]
    return Q.Bool(should=match_queries)


def content_query(search_term: str, model: SupervisedModel) -> Q.Query:
    """
    Defines the ONS conceptual search content query
    :param search_term:
    :param model:
    :return:
    """
    # First, clean the search term and replace all nouns with singulars
    clean_search_term = replace_nouns_with_singulars(clean_string(search_term))

    if len(clean_search_term) == 0:
        raise MalformedSearchTerm(search_term)
