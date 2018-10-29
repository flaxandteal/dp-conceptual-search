"""
Tests the ONS featured result search API
"""
from json import dumps

from unittest import mock
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from unit.utils.test_app import TestApp

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.api.search.list_type import ListType
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.type_filter import AvailableTypeFilters
from dp_conceptual_search.ons.search.sort_fields import query_sort, SortField
from dp_conceptual_search.ons.search.queries.ons_query_builders import content_query
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

        # Build post JSON
        data = {
            "sort_by": sort_by.name
        }

        # URL encode
        url_encoded_params = self.url_encode(params)

        # Use the ONS list_type only
        list_type: ListType = ListType.ONS
        target = "/search/{list_type}/featured?{q}".format(list_type=list_type.name.lower(), q=url_encoded_params)

        # Make the request
        request, response = self.post(target, 200, data=dumps(data))

        # Build the filter query
        type_filters = [
            AvailableTypeFilters.FEATURED.value
        ]
        content_type_filters = []
        for type_filter in type_filters:
            for content_type in type_filter.get_content_types():
                content_type_filters.append(content_type.value.name)
        filter_query = [
            {
                "terms": {
                    "type": content_type_filters
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
