"""
Tests the ONS content search API
"""
from typing import List
from numpy import array

from unittest import mock
from unit.utils.search_test_app import SearchTestApp
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client, mock_hits_highlighted

from dp_fasttext.client.testing.mock_client import mock_labels_api, mock_sentence_vector, mock_fasttext_client

from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.fields import get_highlighted_fields, Field
from dp_conceptual_search.ons.search.content_type import ContentType, AvailableContentTypes
from dp_conceptual_search.ons.conceptual.client import FastTextClientService, ConceptualSearchEngine


class SearchContentApiTestCase(SearchTestApp):

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

    @property
    def highlight_dict(self):
        """
        Builds the expected highlight query dict
        :return:
        """
        highlight_fields: List[Field] = get_highlighted_fields()

        highlight_query = {
            "fields": {
                highlight_field.name: {
                    "number_of_fragments": 0,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                } for highlight_field in highlight_fields
            }
        }

        return highlight_query

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
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

        # Fasttext params
        fasttext_request_data = {
            "query": params.get("q")
        }
        labels_json = mock_labels_api()
        search_vector_json = mock_sentence_vector(fasttext_request_data)

        self.assertIn("labels", labels_json, "fasttext labels json should contain key 'labels'")
        self.assertIn("probabilities", labels_json, "fasttext labels json should contain key 'probabilities'")
        labels = labels_json.get("labels")

        self.assertIn("query", search_vector_json, "fasttext search_vector json should contain key 'query'")
        self.assertIn("vector", search_vector_json, "fasttext search_vector json should contain key 'vector'")
        self.assertEqual(search_vector_json.get("query"), params.get("q"), "fastText query string should match input")
        search_vector = array(search_vector_json.get("vector"))

        # Loop over list types
        target = "/search/conceptual/content?{q}".format(q=url_encoded_params)

        # Make the request
        request, response = self.post(target, 200)

        # Get a list of all available content types
        content_types: List[ContentType] = AvailableContentTypes.available_content_types()

        # Build the expected query dict - note this should not change
        s = ConceptualSearchEngine().content_query(
            self.search_term,
            current_page,
            size,
            highlight=True,
            filter_functions=None,
            type_filters=content_types,
            labels=labels,
            search_vector=search_vector
        )

        expected = s.to_dict()

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        data = response.json
        results = data['results']

        expected_hits_highlighted = mock_hits_highlighted()
        self.assertEqual(results, expected_hits_highlighted, "returned hits should match expected")
