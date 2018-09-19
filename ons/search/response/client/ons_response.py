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

    def to_type_counts_query_search_result(self) -> SearchResult:
        """
        Converts an Elasticsearch response into a TypeCountsQueryResult
        :param doc_counts:
        :return:
        """
        from ons.search.response.type_counts_query_result import TypeCountsQueryResult

        result: TypeCountsQueryResult = TypeCountsQueryResult(self.aggregations)
        return result

    def to_content_query_search_result(self, page_number: int, page_size: int, sort_by: SortFields) -> SearchResult:
        """
        Converts an Elasticsearch response into a ContentQueryResult
        :param page_number:
        :param page_size:
        :param sort_by:
        :return:
        """
        from ons.search.response.content_query_result import ContentQueryResult

        hits = self.hits_to_json()

        paginator = Paginator(
            self.hits.total,
            MAX_VISIBLE_PAGINATOR_LINK,
            page_number,
            page_size)

        result: ContentQueryResult = ContentQueryResult(
            self.hits.total,
            self.took,
            hits,
            paginator,
            sort_by
        )

        return result
