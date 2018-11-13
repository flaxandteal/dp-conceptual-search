"""
Tests all routes on the /search/recommend API
"""
from json import dumps
from typing import List
from unittest import mock
from numpy import ndarray

from unit.utils.search_test_app import SearchTestApp
from unit.elasticsearch.elasticsearch_test_utils import mock_hits_highlighted

from unit.ons.recommend.client.test_recommend_search_client import (
    mock_recommend_search_client, TEST_URI, TEST_HIT_FOR_URI
)

from dp_fasttext.ml.utils import decode_float_list
from dp_fasttext.client.testing.mock_client import mock_similar_vector, mock_fasttext_client

from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService

from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.ons.search.sort_fields import query_sort, SortField
from dp_conceptual_search.ons.recommend.queries.ons_query_builders import similar_to_uri
from dp_conceptual_search.ons.conceptual.client.fasttext_client import FastTextClientService
from dp_conceptual_search.ons.search.fields import get_highlighted_fields, Field, AvailableFields


class RecommendApiTestCase(SearchTestApp):

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

    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_recommend_search_client)
    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    def test_similar_by_uri_api(self):
        """
        Tests the /search/recommend/similar API
        :return:
        """
        # Make the request
        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        # Get test vector
        embedding_field: Field = AvailableFields.EMBEDDING_VECTOR.value

        test_hits: list = TEST_HIT_FOR_URI
        test_hit_source: dict = test_hits[0].get("_source")
        test_hit_vector_encoded = test_hit_source.get(embedding_field.name)
        test_hit_vector_decoded: ndarray = decode_float_list(test_hit_vector_encoded)

        vector_script_score = VectorScriptScore(embedding_field.name, test_hit_vector_decoded)

        num_labels = 10
        mock_similar_by_json = mock_similar_vector()
        mock_similar_by = mock_similar_by_json.get("words")

        # Set sort_by
        sort_by: SortField = SortField.relevance

        # Remove prefix /
        target_uri = TEST_URI[1:]

        # Build params dict
        params = {
            "page": current_page,
            "size": size
        }

        # URL encode
        url_encoded_params = self.url_encode(params)

        # Build post JSON
        data = {
            "uri": target_uri,
            "num_labels": num_labels,
            "sort_by": sort_by.name
        }

        # Set the target
        target = "/search/recommend/similar?{q}".format(q=url_encoded_params)

        # Build the expected query dict - note this should not change
        expected = {
            "query": similar_to_uri(TEST_URI, mock_similar_by, vector_script_score).to_dict(),
            "from": from_start,
            "size": size,
            "highlight": self.highlight_dict,
            "sort": query_sort(SortField.relevance)
        }

        # Make the request
        request, response = self.post(target, 200, data=dumps(data))

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        data = response.json
        results = data['results']

        expected_hits_highlighted = mock_hits_highlighted()
        self.assertEqual(results, expected_hits_highlighted, "returned hits should match expected")