"""
Class to define the structure of an ONS search result
"""
from ons.search.paginator import Paginator
from ons.search.sort_fields import SortFields


class SearchResult(object):
    def __init__(self, number_of_results: int, took: int, results: list, doc_counts: dict,
                 paginator: Paginator, sort_by: SortFields):
        self.number_of_results = number_of_results
        self.took = took
        self.results = results
        self.doc_counts = doc_counts
        self.paginator = paginator
        self.sort_by = sort_by

    def to_dict(self) -> dict:
        return {
            "numberOfResults": self.number_of_results,
            "took": self.took,
            "results": self.results,
            "docCounts": self.doc_counts,
            "paginator": self.paginator.to_dict(),
            "sortBy": self.sort_by.name
        }