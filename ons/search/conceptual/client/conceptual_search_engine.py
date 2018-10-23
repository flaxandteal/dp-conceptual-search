"""
Implementation of conceptual search client
"""
from typing import List

from config import CONFIG

from search.search_type import SearchType

from ons.search.client.search_engine import SearchEngine
from ons.search import SortField, AvailableTypeFilters, TypeFilter, AvailableContentTypes
from ons.search.ons_queries import function_score_content_query

from ons.search.conceptual.queries.ons_queries import content_query

from app.ml.supervised_models_cache import get_supervised_model

from ml.word_embedding.fastText.supervised import SupervisedModel


class ConceptualSearchEngine(SearchEngine):

    def content_query(self, search_term: str, current_page: int, size: int,
                      sort_by: SortField=SortField.relevance,
                      highlight: bool=True,
                      filter_functions: List[AvailableContentTypes]=None,
                      type_filters: List[TypeFilter]=None,
                      **kwargs):
        """
        Builds the ONS conceptual search content query, responsible for populating the SERP
        :param search_term:
        :param current_page:
        :param size:
        :param sort_by:
        :param highlight:
        :param filter_functions:
        :param type_filters:
        :param kwargs:
        :return:
        """
        model: SupervisedModel = get_supervised_model(CONFIG.ML.supervised_model_filename)

        if type_filters is None:
            type_filters = AvailableTypeFilters.all()

        # Build the query dict
        query = content_query(search_term, model)

        # Add function scores if specified
        if filter_functions is not None:
            query = function_score_content_query(query, filter_functions)

        # Build the content query
        s: ConceptualSearchEngine = self._clone() \
            .query(query) \
            .paginate(current_page, size) \
            .sort_by(sort_by) \
            .type_filter(type_filters) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH)

        if highlight:
            s: SearchEngine = s.apply_highlight_fields()

        return s
