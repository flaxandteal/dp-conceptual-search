"""
Class to define the structure of an ONS type counts query search result
"""
from elasticsearch_dsl.response import AggResponse

from dp_conceptual_search.ons.search.response import SearchResult


class TypeCountsQueryResult(SearchResult):

    def __init__(self, aggregations: AggResponse):

        self.aggregations = aggregations
        self._aggs_json = None

        # Build JSON
        total, result = self.aggs_to_json()

        self._data = {
            self.number_of_results_key: total,
            self.doc_counts_key: result
        }

    def aggs_to_json(self):
        if self._aggs_json is None:
            self._aggs_json = self._aggs_to_json()
        return self._aggs_json

    def _aggs_to_json(self) -> (int, dict):
        """
        Converts aggregations response to JSON
        :return:
        """
        # Parse aggregations response
        total = 0
        result = {}
        if hasattr(self.aggregations, self.doc_counts_key):
            aggs = self.aggregations.__dict__["_d_"][self.doc_counts_key]
            buckets = aggs["buckets"]

            # Iterate over buckets
            for item in buckets:
                item_key = item["key"]
                count = item["doc_count"]
                result[item_key] = count
                total += count

        return total, result

    def to_dict(self)-> dict:
        """
        Converts the type counts results to a properly formatted JSON response
        :return:
        """
        return self._data
