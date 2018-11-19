"""
Tests the ONS search engine functionality
"""
from typing import List
from unittest import TestCase

from unit.utils.async_test import AsyncTestCase
from unit.elasticsearch.elasticsearch_test_utils import mock_search_client

from dp_conceptual_search.config import SEARCH_CONFIG
from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.ons.search.client.search_engine import SearchEngine
from dp_conceptual_search.ons.search.sort_fields import query_sort, SortField
from dp_conceptual_search.ons.search.fields import get_highlighted_fields, Field
from dp_conceptual_search.ons.search.type_filter import AvailableTypeFilters, AvailableContentTypes, ContentType
from dp_conceptual_search.ons.search.queries.ons_query_builders import build_content_query, build_type_counts_query


class SearchEngineTestCase(AsyncTestCase, TestCase):

    def setUp(self):
        super(SearchEngineTestCase, self).setUp()

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

    def get_search_engine(self) -> SearchEngine:
        """
        Create an instance of a SearchEngine for testing
        :return:
        """
        engine = SearchEngine(using=self.mock_client, index=self.index)
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

    def test_sort_by(self):
        """
        Tests that the sort by method builds the correct query dictionary
        :return:
        """

        # Loop over all possible sort options
        for sort_by in SortField:
            # Create an instance of the SearchEngine
            engine = self.get_search_engine()

            # Call sort_by
            engine: SearchEngine = engine.sort_by(sort_by)

            # Convert to dictionary
            engine_dict = engine.to_dict()

            # Make sure it matches expected query
            expected = {
                "query": {
                    "match_all": {}
                },
                "sort": query_sort(sort_by)
            }

            for key in expected:
                self.assertIn(key, engine_dict, "key '{0}' should exist in engine dict".format(key))
                self.assertEqual(expected[key], engine_dict[key],
                                 "value for key '{0}' should match expected value".format(key))

    def test_paginate(self):
        """
        Tests that the paginate method works as expected
        :return:
        """
        # Create an instance of the SearchEngine
        engine = self.get_search_engine()

        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        # Call paginate
        engine: SearchEngine = engine.paginate(current_page, size)

        # Convert to dictionary
        engine_dict = engine.to_dict()
        self.assertIsNotNone(engine_dict, "engine dict should not be none")

        # Assert correct query structure
        expected = {
            "from": from_start,
            "query": {
                "match_all": {}
            },
            "size": size
        }

        self.assertEqual(expected, engine_dict, "expected query dict should match actual")

    def test_departments_query(self):
        """
        Tests the departments query method correctly calls the underlying Elasticsearch client
        :return:
        """
        # Create an instance of the SearchEngine
        engine = self.get_search_engine()

        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        # Build the expected query dict - note this should not change
        expected = {
            "from": from_start,
            "query": {
                "match": {
                    "terms": {
                        "query": self.search_term,
                        "type": "boolean"
                    }
                }
            },
            "size": size
        }

        # Call departments_query
        engine: SearchEngine = engine.departments_query(self.search_term, current_page, size)

        # Define the async function to be ran
        async def async_test_function():
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the above function in a dedicated event loop
        self.run_async(async_test_function)

    def test_content_query(self):
        """
        Tests the content query method correctly calls the underlying Elasticsearch client
        :return:
        """
        # Create an instance of the SearchEngine
        engine = self.get_search_engine()

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

        # Build the expected query dict - note this should not change
        expected = {
            "from": from_start,
            "query": {
                "bool": {
                    "filter": filter_query,
                    "must": [
                        build_content_query(self.search_term).to_dict(),
                    ]
                }
            },
            "size": size,
            "sort": query_sort(SortField.relevance),
            "highlight": self.highlight_dict
        }

        # Call departments_query
        engine: SearchEngine = engine.content_query(self.search_term, current_page, size, type_filters=content_types)

        # Define the async function to be ran
        async def async_test_function():
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
        # Create an instance of the SearchEngine
        engine = self.get_search_engine()

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

        aggs_query = build_type_counts_query().to_dict()

        # Build expected aggs query
        aggs = {
            "docCounts": aggs_query
        }

        # Build the expected query dict - note this should not change
        expected = {
            "from": from_start,
            "query": {
                "bool": {
                    "filter": filter_query,
                    "must": [
                        build_content_query(self.search_term).to_dict(),
                    ]
                }
            },
            "size": size,
            "sort": query_sort(SortField.relevance),
            "aggs": aggs
        }

        # Call departments_query
        engine: SearchEngine = engine.type_counts_query(self.search_term, type_filters=content_types)

        # Define the async function to be ran
        async def async_test_function():
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the above function in a dedicated event loop
        self.run_async(async_test_function)

    def test_featured_query(self):
        """
        Tests the featured query method correctly calls the underlying Elasticsearch client
        :return:
        """
        # Create an instance of the SearchEngine
        engine = self.get_search_engine()

        # Set correct from_start and page size for featured result query
        from_start = 0
        size = 1

        # Build the filter query
        content_types = AvailableTypeFilters.FEATURED.value.get_content_types()
        type_filters = [content_type.name for content_type in content_types]
        filter_query = [
            {
                "terms": {
                    "type": type_filters
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
                        build_content_query(self.search_term).to_dict(),
                    ]
                }
            },
            "size": size,
            "sort": query_sort(SortField.relevance)
        }

        # Call departments_query
        engine: SearchEngine = engine.featured_result_query(self.search_term)

        # Define the async function to be ran
        async def async_test_function():
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the above function in a dedicated event loop
        self.run_async(async_test_function)

