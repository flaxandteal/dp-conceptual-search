"""
Defines the base ONS search result
"""
import abc


class SearchResult(abc.ABC):

    number_of_results_key = "numberOfResults"
    took_key = "took"
    results_key = "results"
    paginator_key = "paginator"
    sort_by_key = "sortBy"
    doc_counts_key = "docCounts"

    @abc.abstractmethod
    def to_dict(self) -> dict:
        """
        Converts the search results to a properly formatted JSON response
        :return:
        """
        pass
