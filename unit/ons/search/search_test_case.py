from typing import List

from ons.search.sort_fields import SortField
from ons.search.content_type import ContentTypes
from ons.search.type_filter import TypeFilter
from ons.search.client.search_engine import SearchEngine

from unit.utils.elasticsearch_test_case import ElasticsearchTestCase


class SearchTestCase(ElasticsearchTestCase):
    """
    Contain common (useful) methods for testing search
    """
    @property
    def get_body(self):
        """
        Test query body
        :return:
        """
        body = {
            "query": {
                "match": {
                    "name": "Peter Venkman"
                }
            }
        }
        return body

    @property
    def index(self):
        """
        Returns the test index
        :return:
        """
        return "test"

    @property
    def search_term(self):
        """
        Search term for testing
        :return:
        """
        return "Who ya gonna call?"

    @property
    def type_filters(self) -> List[TypeFilter]:
        """
        Returns a list of type filters for testing
        :return:
        """
        from ons.search.type_filter import TypeFilters

        # Get list of all type filters
        type_filters = TypeFilters.all()

        return type_filters

    @property
    def content_types(self) -> List[ContentTypes]:
        """
        Content type list for testing
        :return:
        """

        # Build up the list of content types for filtering
        content_types = []
        for type_filter in self.type_filters:
            type_filter_content_types = type_filter.get_content_types()
            content_types.extend(type_filter_content_types)

        return content_types

    def get_search_engine(self) -> SearchEngine:
        """
        Create an instance of a SearchEngine for testing
        :return:
        """
        engine = SearchEngine(using=self.mock_client, index=self.index)
        return engine

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

    def expected_departments_query(self, from_start: int, size: int, query_dict: dict) -> dict:
        """
        Returns the expected query body for the given query dictionary
        :param from_start:
        :param size:
        :param query_dict:
        :param sort_by:
        :return:
        """
        expected = {
            "from": from_start,
            "query": {
                **query_dict
            },
            "size": size
        }

        return expected

    def expected_content_query(self, from_start: int, size: int, query_dict: dict, sort_by: SortField) -> dict:
        """
        Returns the expected query body for the given query dictionary
        :param from_start:
        :param size:
        :param query_dict:
        :param sort_by:
        :return:
        """
        from ons.search.sort_fields import query_sort

        expected = {
            "from": from_start,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "type": [content_type.name for content_type in self.content_types]
                            }
                        }
                    ],
                    "must": [
                        query_dict
                    ]
                }
            },
            "size": size,
            "sort": query_sort(sort_by)
        }

        return expected

    def expected_type_counts_query(self, query_dict: dict, sort_by: SortField) -> dict:
        """
        Returns the expected query body for the given query dictionary
        :param query_dict:
        :param sort_by:
        :return:
        """
        from ons.search.queries import type_counts_query
        from ons.search.paginator import RESULTS_PER_PAGE

        # Calculate correct start page number
        current_page = SearchEngine.default_page_number
        size = RESULTS_PER_PAGE
        from_start = 0 if current_page <= 1 else (current_page - 1) * size

        # Build the expected query dict - note this should not change
        expected = self.expected_content_query(from_start, size, query_dict, sort_by)

        # Add expected aggregations
        expected["aggs"] = {
            SearchEngine.agg_bucket: type_counts_query().to_dict()
        }

        return expected

    def expected_featured_result_query(self, query_dict: dict) -> dict:
        """
        Returns the expected query body for the given query dictionary
        :param query_dict:
        :return:
        """
        from ons.search.sort_fields import query_sort
        from ons.search.type_filter import TypeFilters

        # Setup expected content types filter
        type_filter: TypeFilter = TypeFilters.FEATURED.value
        content_types: List[ContentTypes] = type_filter.get_content_types()

        # Expected from_start and page size params
        from_start = 0
        size = 1

        expected = {
            "from": from_start,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "type": [content_type.name for content_type in content_types]
                            }
                        }
                    ],
                    "must": [
                        query_dict
                    ]
                }
            },
            "size": size,
            "sort": query_sort(SortField.relevance)
        }

        return expected

    def setUpContentQuery(self, sort_by: SortField, filter_by_content_types: List[ContentTypes]=None):
        """
        Builds a SearchEngine instance and sets up the content query
        :return:
        """
        from ons.search.queries import content_query, function_score_content_query

        # Create instance of SearchEngine
        engine = self.get_search_engine()

        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        # Build the content query and convert to dict
        query = content_query(self.search_term)

        if filter_by_content_types is not None:
            # Add filter functions
            query = function_score_content_query(query, filter_by_content_types)

        # Get the resulting query dict
        query_dict = query.to_dict()

        # Build the expected query dict - note this should not change
        expected = self.expected_content_query(from_start, size, query_dict, sort_by)

        # Call content_query
        engine: SearchEngine = engine.content_query(self.search_term,
                                                    current_page,
                                                    size,
                                                    sort_by=sort_by,
                                                    type_filters=self.type_filters,
                                                    filter_functions=filter_by_content_types)

        # Assert correct dict structure
        engine_dict = engine.to_dict()
        self.assertEqualDicts(expected, engine_dict)

        return engine, expected

    def assertEqualDicts(self, first: dict, second: dict):
        """
        Asserts two dics are equal without requiring same ordering
        :param first:
        :param second:
        :return:
        """
        for key in first:
            self.assertIn(key, second, "key '{0}' should exist in engine dict".format(key))
            self.assertEqual(first[key], second[key],
                             "value for key '{0}' should match expected value".format(key))