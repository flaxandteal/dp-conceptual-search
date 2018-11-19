import abc
import logging as logger
from typing import List

from dp_conceptual_search.search.client.search_client import SearchClient

from dp_conceptual_search.ons.search.sort_fields import query_sort
from dp_conceptual_search.ons.search import ContentType, SortField
from dp_conceptual_search.ons.search.fields import get_highlighted_fields, Field
from dp_conceptual_search.ons.search.response.client.ons_response import ONSResponse


class AbstractSearchEngine(SearchClient, abc.ABC):
    """
    Abstract search engine client defining common methods for ONS search engine
    """
    def __init__(self, **kwargs):
        super(AbstractSearchEngine, self).__init__(response_class=ONSResponse, **kwargs)

    def apply_highlight_fields(self):
        """
        Applies highlight options to the Elasticsearch query
        :return:
        """
        highlight_fields: List[Field] = get_highlighted_fields()

        # Get the field names
        field_names = [field.name for field in highlight_fields]

        # Apply to query
        return self.highlight(
            *field_names,
            number_of_fragments=0,  # return whole field with highlighting
            pre_tags=["<strong>"],
            post_tags=["</strong>"])

    def sort_by(self, sort_by: SortField):
        """
        Adds sort options to query
        :param sort_by:
        :return:
        """
        return self.sort(
            *query_sort(sort_by)
        )

    def type_filter(self, type_filters: List[ContentType]):
        """
        Add type filter options to the query
        :param type_filters:
        :return:
        """
        if not isinstance(type_filters, list) or len(type_filters) == 0 or not isinstance(type_filters[0], ContentType):
            logger.error("Method 'type_filter' requires List[ContentType]")
            raise ValueError("Method 'type_filter' requires List[ContentType]")

        type_filters_list: List[str] = [content_type.name for content_type in type_filters]
        return self.filter("terms", type=type_filters_list)

    def paginate(self, current_page: int, size: int):
        """
        Add pagination options to the query.
        :param current_page:
        :param size:
        :return:
        """
        s: AbstractSearchEngine = self._clone()

        # Calculate from_start param
        from_start = 0 if current_page <= 1 else (current_page - 1) * size
        end = from_start + size

        return s[from_start:end]

    @abc.abstractmethod
    def departments_query(
            self,
            search_term: str,
            current_page: int,
            size: int):
        """
        ONS departments query
        :param search_term:
        :param current_page:
        :param size:
        :return:
        """
        pass

    @abc.abstractmethod
    def content_query(self, search_term: str, current_page: int, size: int,
                      sort_by: SortField=SortField.relevance,
                      highlight: bool=True,
                      filter_functions: List[ContentType]=None,
                      type_filters: List[ContentType]=None,
                      **kwargs):
        """
        Builds the ONS content query, responsible for populating the SERP
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
        pass

    @abc.abstractmethod
    def type_counts_query(self, search_term, type_filters: List[ContentType]=None, **kwargs):
        """
        Builds the ONS type counts query, responsible providing counts by content type
        :param search_term:
        :param type_filters:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def featured_result_query(self, search_term):
        """
        ONS query for featured pages
        :param search_term:
        :return:
        """
        pass
