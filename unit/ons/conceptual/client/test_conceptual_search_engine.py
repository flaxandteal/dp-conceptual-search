"""
Tests the ONS conceptual search engine functionality
"""
from typing import List
from numpy.random import rand

from unittest import TestCase
from unit.utils.async_test import AsyncTestCase

from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from dp_conceptual_search.search.search_type import SearchType

from dp_conceptual_search.config import SEARCH_CONFIG
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search.content_type import AvailableContentTypes, ContentType
from dp_conceptual_search.ons.conceptual.queries.ons_query_builders import build_content_query
from dp_conceptual_search.ons.search.queries.ons_query_builders import build_type_counts_query
from dp_conceptual_search.ons.search.fields import get_highlighted_fields, Field, AvailableFields
from dp_conceptual_search.ons.conceptual.client.conceptual_search_engine import ConceptualSearchEngine


class ConceptualSearchEngineTestCase(AsyncTestCase, TestCase):

    def setUp(self):
        super(ConceptualSearchEngineTestCase, self).setUp()

        self.mock_client = mock_search_client()

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

    def get_search_engine(self) -> ConceptualSearchEngine:
        """
        Create an instance of a SearchEngine for testing
        :return:
        """
        engine = ConceptualSearchEngine(using=self.mock_client, index=self.index)
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

    def test_content_query(self):
        """
        Tests the content query method correctly calls the underlying Elasticsearch client
        :return:
        """
        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        # Get a list of all available content types
        content_types: List[ContentType] = AvailableContentTypes.available_content_types()

        # Build the filter query
        type_filters = [content_type.name for content_type in content_types]
        filter_query = [
            {
                "terms": {
                    "type": type_filters
                }
            }
        ]

        vector = rand(10)
        embedding_field: Field = AvailableFields.EMBEDDING_VECTOR.value
        vector_script_score: VectorScriptScore = VectorScriptScore(embedding_field.name, vector)

        labels = ["these", "are", "a", "test"]

        # Build the expected query dict - note this should not change
        expected = {
            "query": {
                "bool": {
                    "filter": filter_query,
                    "must": [
                        build_content_query(self.search_term, labels, vector_script_score).to_dict(),
                    ]
                }
            },
            "from": from_start,
            "size": size,
            "_source": {
                "exclude": [embedding_field.name]
            },
            "highlight": self.highlight_dict
        }

        # Define the async function to be ran
        async def async_test_function():
            # Create an instance of the SearchEngine
            engine = self.get_search_engine()

            engine: ConceptualSearchEngine = engine.content_query(self.search_term, current_page, size,
                                                                  labels=labels, search_vector=vector,
                                                                  type_filters=content_types)

            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the above function in a dedicated event loop
        self.run_async(async_test_function)

    def test_type_counts_query(self):
        """
        Tests the type counts query method correctly calls the underlying Elasticsearch client
        :return:
        """
        # Set correct from_start and page size for type counts query
        from_start = 0
        size = SEARCH_CONFIG.results_per_page

        # Get a list of all available content types
        content_types: List[ContentType] = AvailableContentTypes.available_content_types()

        # Build the filter query
        type_filters = [content_type.name for content_type in content_types]
        filter_query = [
            {
                "terms": {
                    "type": type_filters
                }
            }
        ]

        # Build expected aggs query
        aggs = {
            "docCounts": build_type_counts_query().to_dict()
        }

        vector = rand(10)
        embedding_field: Field = AvailableFields.EMBEDDING_VECTOR.value
        vector_script_score: VectorScriptScore = VectorScriptScore(embedding_field.name, vector)

        labels = ["these", "are", "a", "test"]

        # Build the expected query dict - note this should not change
        expected = {
            "query": {
                "bool": {
                    "filter": filter_query,
                    "must": [
                        build_content_query(self.search_term, labels, vector_script_score).to_dict(),
                    ]
                }
            },
            "from": from_start,
            "size": size,
            "_source": {
                "exclude": [embedding_field.name]
            },
            "aggs": aggs
        }

        # Define the async function to be ran
        async def async_test_function():
            # Create an instance of the SearchEngine
            engine = self.get_search_engine()

            engine: ConceptualSearchEngine = engine.type_counts_query(self.search_term, labels=labels,
                                                                      search_vector=vector, type_filters=content_types)
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the above function in a dedicated event loop
        self.run_async(async_test_function)
