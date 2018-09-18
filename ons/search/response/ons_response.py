from elasticsearch_dsl.response import Response

from ons.search.sort_fields import SortFields
from ons.search.response.search_result import SearchResult
from ons.search.paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK


class ONSResponse(Response):

    def hits_to_json(self) -> list:
        """
        Converts the search hits to a list of JSON
        :return:
        """
        return [hit.to_dict() for hit in self.hits]

    def to_search_result(self, page_number: int, page_size: int, sort_by: SortFields, doc_counts: dict={}) -> SearchResult:
        """
        Converts an Elasticsearch response into a SearchResult
        :param page_number:
        :param page_size:
        :param sort_by:
        :param doc_counts:
        :return:
        """

        hits = self.hits_to_json()

        paginator = Paginator(
            self.hits.total,
            MAX_VISIBLE_PAGINATOR_LINK,
            page_number,
            page_size)

        result: SearchResult = SearchResult(
            self.hits.total,
            self.took,
            hits,
            doc_counts,
            paginator,
            sort_by
        )

        return result
