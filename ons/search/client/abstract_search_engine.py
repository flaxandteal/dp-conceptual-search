import abc
from typing import List

from core.search.client import SearchClient
from ons.search.sort_fields import SortFields
from ons.search.type_filter import TypeFilters


class AbstractSearchEngine(SearchClient, abc.ABC):
    """
    Abstract search engine client defining common methods for ONS search engine
    """
    def __init__(self, **kwargs):
        from ons.search.response import ONSResponse

        super(AbstractSearchEngine, self).__init__(response_class=ONSResponse, **kwargs)

    def sort_by(self, sort_by: SortFields):
        """
        Adds sort options to query
        :param sort_by:
        :return:
        """
        from ons.search.sort_fields import query_sort

        return self.sort(
            *query_sort(sort_by)
        )

    def type_filter(self, type_filters: List[TypeFilters]):
        """
        Add type filter options to the query
        :param type_filters:
        :return:
        """
        type_filter_list = []
        for type_filter in type_filters:
            for content_type in type_filter.value.get_content_types():
                type_filter_list.append(content_type.name)

        return self.filter("terms", type=type_filter_list)

    def paginate(self, current_page: int, size: int):
        """
        Add pagination options to the query
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
    def content_query(
            self,
            search_term: str,
            current_page: int,
            size: int,
            **kwargs):
        """
        ONS search query to populate the SERP
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """
        pass

    @abc.abstractmethod
    def type_counts_query(
            self,
            search_term,
            **kwargs):
        """
        ONS aggregations query to compute _type counts
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
