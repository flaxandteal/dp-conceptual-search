"""
Tests the ONS type counts search API
"""
from json import dumps
from typing import List

from unittest import mock

from unit.utils.search_test_app import SearchTestApp
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.sort_fields import query_sort, SortField
from dp_conceptual_search.ons.search.content_type import AvailableContentTypes, ContentType
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService
from dp_conceptual_search.ons.search.queries.ons_query_builders import build_content_query, build_type_counts_query


class SearchTypeCountsApiTestCase(SearchTestApp):

    # @staticmethod
    # def paginate():
    #     """
    #     Calls paginate and makes some basic assertions
    #     :return:
    #     """
    #     import random
    #
    #     # Generate a random page number between 1 and 10
    #     current_page = random.randint(1, 10)
    #
    #     # Generate a random page size between 11 and 20
    #     size = random.randint(11, 20)
    #
    #     # Calculate correct start page number
    #     from_start = 0 if current_page <= 1 else (current_page - 1) * size
    #
    #     return from_start, current_page, size

    @property
    def search_term(self):
        """
        Mock search term to be used for testing
        :return:
        """
        return "Zuul"

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_type_counts_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a type counts query
        :return:
        """
        # Make the request
        # Set correct from_start and page size for type counts query
        from_start = 0
        current_page = 0
        size = 0

        # Set sort_by
        sort_by: SortField = SortField.relevance

        # Build params dict
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size
        }

        # Build post JSON
        data = {
            "sort_by": sort_by.name
        }

        # URL encode
        url_encoded_params = self.url_encode(params)

        target = "/search/counts?{q}".format(q=url_encoded_params)

        # Make the request
        request, response = self.post(target, 200, data=dumps(data))

        # Get a list of all available content types
        content_types: List[ContentType] = AvailableContentTypes.available_content_types()

        # Build the filter query
        type_filters = [content_type.name for content_type in content_types]
        filter_query = [
            {
                "terms": {
                    "type": type_filters
                }
            }
        ]

        aggs_query = build_type_counts_query().to_dict()

        # Build expected aggs query
        aggs = {
            "docCounts": aggs_query
        }

        # Build the expected query dict - note this should not change
        expected = {
            "from": from_start,
            "query": {
                "bool": {
                    "filter": filter_query,
                    "must": [
                        build_content_query(self.search_term).to_dict(),
                    ]
                }
            },
            "size": size,
            "sort": query_sort(SortField.relevance),
            "aggs": aggs
        }

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)
