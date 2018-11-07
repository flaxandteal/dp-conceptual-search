"""
Tests the ONS content search API
"""
from unittest import mock

from unit.utils.test_app import TestApp
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client, mock_hits_highlighted

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SearchDepartmentsApiTestCase(TestApp):

    maxDiff = None

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
        return "Education"

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_content_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a content query
        :return:
        """
        # Make the request
        # Set pagination params
        from_start, current_page, size = self.paginate()

        # Build params dict
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size
        }

        # URL encode
        url_encoded_params = self.url_encode(params)

        target = "/search/ons/departments?{q}".format(q=url_encoded_params)

        # Make the request
        request, response = self.get(target, 200)

        # Build the expected query dict - note this should not change
        expected = {
            "query": {
                "match": {
                    "terms": {
                        "query": self.search_term,
                        "type": "boolean"
                    }
                }
            },
            "from": from_start,
            "size": size
        }

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.DEPARTMENTS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        data = response.json
        results = data['results']

        expected_hits_highlighted = mock_hits_highlighted()
        self.assertEqual(results, expected_hits_highlighted, "returned hits should match expected")



