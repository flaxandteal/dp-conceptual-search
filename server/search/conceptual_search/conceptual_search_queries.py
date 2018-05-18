from elasticsearch_dsl import query

from server.search import fields
from server.word_embedding.supervised_models import SupervisedModel


def word_vector_keywords_query(
        search_term: str,
        model: SupervisedModel) -> query.Query:
    search_vector = model.get_sentence_vector(search_term)
    additional_keywords, similarity = model.get_labels_for_vector(
        search_vector, 10)
    additional_keywords = [k.replace("_", " ")
                           for k in additional_keywords]

    # Add query to dis_max
    keywords_query = query.Bool(should=[query.Match(
        **{fields.keywords.name: k}) for k in additional_keywords])
    return keywords_query
