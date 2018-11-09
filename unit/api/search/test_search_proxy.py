"""
Tests the ONS proxy search API
"""
from json import dumps
from unit.utils.search_test_app import SearchTestApp

from unittest import mock

from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from dp_conceptual_search.config import CONFIG
from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SearchProxyApiTestCase(SearchTestApp):

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

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_proxy_api_raises_400(self):
        """
        Tests that the proxy search API raises a 400 when no query body is specified (or the 'query' key doesn't exist)
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        params = {
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/?{0}".format(url_encoded_params)

        # Make the request
        request, response = self.post(target, 400)

        # Specify data but with no query key
        # Build expected query
        # Build the content query and convert to dict
        query = {
            "query" : {
                "match": {
                    "name": "Zuul"
                }
            }
        }

        post_params = {
            "wrong_key": dumps(query)
        }
        # Make the request
        request, response = self.post(target, 400, data=dumps(post_params))

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_proxy_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a proxy query
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        params = {
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/?{0}".format(url_encoded_params)

        # Build expected query
        # Build the content query and convert to dict
        query = {
            "query": {
                "match": {
                    "name": "Zuul"
                }
            }
        }

        post_params = {
            "query": dumps(query)
        }

        # Make the request
        request, response = self.post(target, 200, data=dumps(post_params))

        # Build the expected query dict - note this should not change
        expected = query.copy()
        expected["from"] = from_start
        expected["size"] = size

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected)

    def test_max_request_size_400(self):
        """
        Test that making a request where the page size if greater than the max allowed raises a 400 BAD_REQUEST
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        size = CONFIG.SEARCH.max_request_size + 1

        params = {
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/?{0}".format(url_encoded_params)

        # Build expected query
        # Build the content query and convert to dict
        query = {
            "query": {
                "match": {
                    "name": "Zuul"
                }
            }
        }

        post_params = {
            "query": dumps(query)
        }

        # Make the request
        request, response = self.post(target, 400, data=dumps(post_params))
