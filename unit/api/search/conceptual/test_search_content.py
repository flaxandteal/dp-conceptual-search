"""
Tests the ONS content search API
"""
from json import dumps
from typing import List

from config import CONFIG

from unittest import mock
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client, mock_hits_highlighted

from app.ml.supervised_models_cache import get_supervised_model
from app.elasticsearch.elasticsearch_client_service import ElasticsearchClientService

from unit.utils.test_app import TestApp

from api.search.list_type import ListType

from search.search_type import SearchType

from ons.search.index import Index
from ons.search.content_type import AvailableContentTypes
from ons.search.fields import get_highlighted_fields, Field
from ons.search.conceptual.queries.ons_query_builders import content_query
from ons.search.conceptual.client.conceptual_search_engine import ConceptualSearchEngine


class SearchContentApiTestCase(TestApp):

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
    def test_content_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a content query
        :return:
        """
        # Get cached model
        fname = CONFIG.ML.supervised_model_filename
        model = get_supervised_model(fname)

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

        # Loop over list types
        list_type: ListType
        for list_type in ListType:
            target = "/search/conceptual/{list_type}/content?{q}".format(list_type=list_type.name.lower(), q=url_encoded_params)

            # Make the request
            request, response = self.post(target, 200)

            # Build the filter query
            type_filters = list_type.to_type_filters()

            # Build the expected query dict - note this should not change
            s = ConceptualSearchEngine().content_query(
                self.search_term,
                current_page,
                size,
                highlight=True,
                filter_functions=None,
                type_filters=type_filters
            )

            expected = s.to_dict()

            # Assert search was called with correct arguments
            self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

            data = response.json
            results = data['results']

            expected_hits_highlighted = mock_hits_highlighted()
            self.assertEqual(results, expected_hits_highlighted, "returned hits should match expected")



