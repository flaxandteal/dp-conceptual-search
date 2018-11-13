"""
Tests the ONS type counts search API
"""
from typing import List
from numpy import array

from unittest import mock
from unit.utils.search_test_app import SearchTestApp
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from dp_fasttext.client.testing.mock_client import mock_labels_api, mock_sentence_vector, mock_fasttext_client

from dp_conceptual_search.config import SEARCH_CONFIG
from dp_conceptual_search.ons.search.index import Index
from dp_conceptual_search.api.search.list_type import ListType
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.type_filter import AvailableTypeFilters, TypeFilter
from dp_conceptual_search.ons.search.conceptual.client.fasttext_client import FastTextClientService
from dp_conceptual_search.app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService
from dp_conceptual_search.ons.search.conceptual.client.conceptual_search_engine import ConceptualSearchEngine


class SearchTypeCountsApiTestCase(SearchTestApp):

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

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    @mock.patch.object(ElasticsearchClientService, '_init_client', mock_search_client)
    def test_type_counts_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a type counts query
        :return:
        """
        # Make the request
        # Set correct from_start and page size for type counts query
        from_start = 0
        current_page = from_start + 1
        size = SEARCH_CONFIG.results_per_page

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
        list_type: ListType
        for list_type in ListType:
            target = "/search/conceptual/{list_type}/counts?{q}".format(list_type=list_type.name.lower(), q=url_encoded_params)

            # Make the request
            request, response = self.post(target, 200)

            # Build the filter query - Note, for type counts we use all available type filters (not those
            # specified in the list type)
            type_filters: List[TypeFilter] = AvailableTypeFilters.all()

            # Build the expected query dict - note this should not change
            # Build the expected query dict - note this should not change
            s = ConceptualSearchEngine().type_counts_query(
                self.search_term,
                type_filters=type_filters,
                labels=labels,
                search_vector=search_vector
            )

            expected = s.to_dict()

            # Assert search was called with correct arguments
            self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)
