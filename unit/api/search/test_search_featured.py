"""
Tests the ONS featured result search API
"""
from typing import List

from unittest import mock
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from unit.utils.test_app import TestApp

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.queries import content_query
from dp_conceptual_search.ons.search.content_type import ContentType
from dp_conceptual_search.ons.search.type_filter import AvailableTypeFilters
from dp_conceptual_search.ons.search.sort_fields import query_sort, SortField
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SearchFeaturedApiTestCase(TestApp):

    @staticmethod
    def paginate():
        """
        Calls paginate and makes some basic assertions
        :return:
        """
        import random

        # Generate a random page number between 1 and 10
        current_page = random.randint(1, 10)

        # Generate a random page size between 11 and 20
        size = random.randint(11, 20)

        # Calculate correct start page number
        from_start = 0 if current_page <= 1 else (current_page - 1) * size

        return from_start, current_page, size

    @property
    def search_term(self):
        """
        Mock search term to be used for testing
        :return:
        """
        return "Zuul"

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_featured_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a featured result query
        :return:
        """
        # Make the request
        # Set correct from_start and page size for featured result query
        from_start = 0
        current_page = from_start + 1
        size = 1

        # Set sort_by
        sort_by: SortField = SortField.relevance

        # Build params dict
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size
        }

        # URL encode
        url_encoded_params = self.url_encode(params)

        target = "/search/featured?{q}".format(q=url_encoded_params)

        # Make the request
        request, response = self.get(target, 200)

        # Get a list of all available content types
        content_types: List[ContentType] = AvailableTypeFilters.FEATURED.value.get_content_types()
        type_filters = [content_type.name for content_type in content_types]

        filter_query = [
            {
                "terms": {
                    "type": type_filters
                }
            }
        ]

        # Build the expected query dict - note this should not change
        expected = {
            "from": from_start,
            "query": {
                "bool": {
                    "filter": filter_query,
                    "must": [
                        content_query(self.search_term).to_dict(),
                    ]
                }
            },
            "size": size,
            "sort": query_sort(SortField.relevance)
        }

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)
