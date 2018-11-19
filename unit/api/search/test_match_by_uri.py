"""
Tests the ONS content search API
"""
from unittest import mock

from unit.utils.search_test_app import SearchTestApp
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client, mock_uri_hit

from dp_conceptual_search.ons.search.index import Index

from dp_conceptual_search.search.query_helper import match_by_uri

from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService


class SearchContentApiTestCase(SearchTestApp):

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_content_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a content query
        :return:
        """
        # Make the request

        test_uri = "this/is/a/test/uri"
        target = "/search/uri/{uri}".format(uri=test_uri)

        # Make the request
        request, response = self.post(target, 200)

        # Build the expected query dict - note this should not change
        expected = {
            "query": match_by_uri(test_uri).to_dict()
        }

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected)

        # Get JSON response
        data = response.json
        results = data['results']

        # Build the expected hit object
        hit = mock_uri_hit(test_uri)
        expected_hit = hit.get("_source")
        expected_hit['_type'] = hit.get("_type")

        # The API will return the hit as a singleton list, so wrap in a list for assertion

        self.assertEqual(results, [expected_hit], "returned hits should match expected")
