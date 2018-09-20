from elasticsearch_dsl.response import Response

from ons.search.sort_fields import SortFields
from ons.search.response import SearchResult, ContentQueryResult, TypeCountsQueryResult
from ons.search.paginator import Paginator


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
        result: TypeCountsQueryResult = TypeCountsQueryResult(self.aggregations)
        return result

    def to_featured_result_query_search_result(self) -> SearchResult:
        """
        Converts an Elasticsearch response into a ContentQueryResult
        :return:
        """
        return self.to_content_query_search_result(1, 1, SortFields.relevance)

    def to_content_query_search_result(self, page_number: int, page_size: int, sort_by: SortFields) -> SearchResult:
        """
        Converts an Elasticsearch response into a ContentQueryResult
        :param page_number:
        :param page_size:
        :param sort_by:
        :return:
        """
        hits = self.hits_to_json()

        paginator = Paginator(
            self.hits.total,
            page_number,
            result_per_page=page_size)

        result: ContentQueryResult = ContentQueryResult(
            self.hits.total,
            self.took,
            hits,
            paginator,
            sort_by
        )

        return result
