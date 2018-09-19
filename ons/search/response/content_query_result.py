"""
Class to define the structure of an ONS content query search result
"""
from ons.search.paginator import Paginator
from ons.search.sort_fields import SortFields
from ons.search.response.search_result import SearchResult


class ContentQueryResult(SearchResult):
    def __init__(self, number_of_results: int, took: int, results: list,
                 paginator: Paginator, sort_by: SortFields):

        self.number_of_results = number_of_results
        self.took = took
        self.results = results
        self.paginator = paginator
        self.sort_by = sort_by

        self._data = {
            self.number_of_results_key: self.number_of_results,
            self.took_key: self.took,
            self.results_key: self.results,
            self.paginator_key: self.paginator.to_dict(),
            self.sort_by_key: self.sort_by.name
        }

    def to_dict(self) -> dict:
        """
        Converts the search results to a properly formatted JSON response
        :return:
        """
        return self._data
