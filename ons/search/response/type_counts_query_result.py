"""
Class to define the structure of an ONS type counts query search result
"""
from elasticsearch_dsl.response import AggResponse
from ons.search.response.search_result import SearchResult


class TypeCountsQueryResult(SearchResult):

    def __init__(self, aggregations: AggResponse):

        self.aggregations = aggregations

    def aggs_to_json(self) -> (int, dict):
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
        Converts the search results to a properly formatted JSON response
        :return:
        """

        total, result = self.aggs_to_json()
        return {
            self.number_of_results_key: total,
            self.doc_counts_key: result
        }
