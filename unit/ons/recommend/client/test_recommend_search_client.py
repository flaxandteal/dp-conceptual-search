"""
Tests the ONS recommendation search engine functionality
"""
from typing import List
from numpy import ndarray

from unittest import mock, TestCase
from unittest.mock import MagicMock

from unit.utils.async_test import AsyncTestCase
from unit.elasticsearch.elasticsearch_test_utils import MockElasticsearchClient, mock_hits, mock_single_hit, mock_search_response

from dp_fasttext.ml.utils import decode_float_list
from dp_fasttext.client.testing.mock_client import mock_similar_vector, mock_fasttext_client

from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.search.query_helper import match_by_uri
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search.sort_fields import query_sort, SortField
from dp_conceptual_search.ons.recommend.queries.ons_query_builders import similar_to_uri
from dp_conceptual_search.ons.conceptual.client.fasttext_client import FastTextClientService
from dp_conceptual_search.ons.search.fields import get_highlighted_fields, Field, AvailableFields
from dp_conceptual_search.ons.recommend.client.recommend_search_engine import RecommendationSearchEngine


# Define global test params
TEST_URI = "/this/is/a/test/uri"
TEST_HIT_FOR_URI = mock_single_hit()


# Need a custom mock here to handle match by uri query
def mock_search(index=None, doc_type=None, body=None, params=None, **kwargs):
    """
    Mocks the Elasticsearch client search method
    :param index:
    :param doc_type:
    :param body:
    :param params:
    :return:
    """
    match_query = {
        "query": match_by_uri(TEST_URI).to_dict()
    }

    if body == match_query:
        return mock_search_response(TEST_HIT_FOR_URI)
    else:
        return mock_search_response(mock_hits())


def mock_recommend_search_client(*args):
    """
    Returns a mock client capable of handling match by uri queries
    :return:
    """
    # Mock the search client
    mock_client = MockElasticsearchClient()
    mock_client.search = MagicMock()

    # Set side effect to call mock search method
    mock_client.search.side_effect = mock_search

    return mock_client


# Define the test case
class RecommendationSearchEngineTestCase(AsyncTestCase, TestCase):

    def setUp(self):
        super(RecommendationSearchEngineTestCase, self).setUp()

        self.mock_client = mock_recommend_search_client()

    @property
    def index(self):
        """
        Mock index to be used for testing
        :return:
        """
        return "test"

    @property
    def search_term(self):
        """
        Mock search term to be used for testing
        :return:
        """
        return "Zuul"

    def get_search_engine(self) -> RecommendationSearchEngine:
        """
        Create an instance of a SearchEngine for testing
        :return:
        """
        engine = RecommendationSearchEngine(using=self.mock_client, index=self.index)
        return engine

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

    @mock.patch.object(FastTextClientService, 'get_fasttext_client', mock_fasttext_client)
    def test_similar_by_uri_query(self):
        """
        Tests the similar_by_uri query method correctly calls the underlying Elasticsearch client
        :return:
        """
        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        embedding_field: Field = AvailableFields.EMBEDDING_VECTOR.value

        # Get test vector
        test_hits: list = TEST_HIT_FOR_URI
        test_hit_source: dict = test_hits[0].get("_source")
        test_hit_vector_encoded = test_hit_source.get(embedding_field.name)
        test_hit_vector_decoded: ndarray = decode_float_list(test_hit_vector_encoded)

        vector_script_score = VectorScriptScore(embedding_field.name, test_hit_vector_decoded)

        num_labels = 10
        mock_similar_by_json = mock_similar_vector()
        mock_similar_by = mock_similar_by_json.get("words")

        # Build the expected query dict - note this should not change
        expected = {
            "query": similar_to_uri(TEST_URI, mock_similar_by, vector_script_score).to_dict(),
            "from": from_start,
            "size": size,
            "highlight": self.highlight_dict,
            "sort": query_sort(SortField.relevance)
        }

        # Define the async function to be ran
        async def async_test_function():
            # Create an instance of the SearchEngine
            engine = self.get_search_engine()

            engine: RecommendationSearchEngine = await engine.similar_by_uri_query(TEST_URI, num_labels,
                                                                                   current_page, size)

            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the above function in a dedicated event loop
        self.run_async(async_test_function)