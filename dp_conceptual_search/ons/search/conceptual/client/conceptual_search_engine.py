"""
Implementation of conceptual search client
"""
import logging
from typing import List

from uuid import uuid4

from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.conceptual.queries.ons_query_builders import content_query
from dp_conceptual_search.ons.search import SortField, AvailableTypeFilters, TypeFilter, AvailableContentTypes


def generate_context():
    context = str(uuid4())
    logging.info("No request context specified, generating", extra={
        "context": context
    })

    return context


class ConceptualSearchEngine(SearchEngine):

    async def content_query(self, search_term: str, current_page: int, size: int,
                            sort_by: SortField = SortField.relevance,
                            highlight: bool = True,
                            filter_functions: List[AvailableContentTypes] = None,
                            type_filters: List[TypeFilter] = None,
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
        context = kwargs.get("context", generate_context())

        if sort_by is not SortField.relevance:
            logging.info("SortField != relevance, conceptual search is disabled", extra={
                "context": context,
                "query": search_term,
                "sort_by": sort_by.name
            })

        if type_filters is None:
            logging.info("No type filters specified, using all", extra={
                "context": context
            })
            type_filters = AvailableTypeFilters.all()

        # Build the query dict
        logging.debug("Building conceptual content query", extra={
            "context": context,
            "query": search_term,
            "current_page": current_page,
            "page_size": size
        })
        query = await content_query(search_term, context, **kwargs)

        # Build the content query
        s: ConceptualSearchEngine = self._clone() \
            .query(query) \
            .paginate(current_page, size) \
            .type_filter(type_filters) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH)

        if highlight:
            s: SearchEngine = s.apply_highlight_fields()

        return s
