from typing import List

from ons.search.sort_fields import SortField
from ons.search.content_type import AvailableContentTypes
from ons.search.type_filter import TypeFilter
from ons.search.client.search_engine import SearchEngine
from ons.search.fields import get_highlighted_fields, Field

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

    def expected_highlight_query(self):
        """
        Builds the expected highlight query dict
        :return:
        """
        # Build highlight fields
        highlight_fields: List[Field] = get_highlighted_fields()

        # Get the field names
        field_names = [field.name for field in highlight_fields]

        # Build highlight query object
        field_highlight_queries = {}
        for field_name in field_names:
            field_highlight_queries[field_name] = {
                'number_of_fragments': 0,
                'pre_tags': ['<strong>'],
                'post_tags': ['</strong>']
            }

        highlight_query = {
            "fields": field_highlight_queries
        }

        return highlight_query

    def expected_content_query(self, from_start: int, size: int, query_dict: dict, sort_by: SortField, type_filters: List[TypeFilter]) -> dict:
        """
        Returns the expected query body for the given query dictionary
        :param from_start:
        :param size:
        :param query_dict:
        :param sort_by:
        :param type_filters:
        :return:
        """
        from ons.search.sort_fields import query_sort

        # Build content type from type filters
        content_types: List[AvailableContentTypes] = []
        for type_filter in type_filters:
            content_types.extend(type_filter.get_content_types())

        # Build the highlight query
        highlight_query = self.expected_highlight_query()

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
            "highlight": highlight_query,
            "sort": query_sort(sort_by)
        }

        return expected

    def expected_type_counts_query(self, query_dict: dict, sort_by: SortField, type_filters: List[TypeFilter]) -> dict:
        """
        Returns the expected query body for the given query dictionary
        :param query_dict:
        :param sort_by:
        :param type_filters:
        :return:
        """
        from ons.search.queries import type_counts_query
        from ons.search.paginator import RESULTS_PER_PAGE

        # Calculate correct start page number
        current_page = SearchEngine.default_page_number - 1
        size = RESULTS_PER_PAGE
        from_start = 0 if current_page <= 1 else (current_page - 1) * size

        # Build the expected query dict - note this should not change
        expected = self.expected_content_query(from_start, size, query_dict, sort_by, type_filters)

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
        from ons.search.type_filter import AvailableTypeFilters

        # Setup expected content types filter
        type_filter: TypeFilter = AvailableTypeFilters.FEATURED.value
        content_types: List[AvailableContentTypes] = type_filter.get_content_types()

        # Expected from_start and page size params
        from_start = 0
        size = 1

        # Build the highlight query
        highlight_query = self.expected_highlight_query()

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
            "highlight": highlight_query,
            "sort": query_sort(SortField.relevance)
        }

        return expected

    def setUpContentQuery(self, sort_by: SortField, type_filters: List[TypeFilter], filter_functions: List[AvailableContentTypes]=None):
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

        if filter_functions is not None:
            # Add filter functions
            query = function_score_content_query(query, filter_functions)

        # Get the resulting query dict
        query_dict = query.to_dict()

        # Build the expected query dict - note this should not change
        expected = self.expected_content_query(from_start, size, query_dict, sort_by, type_filters)

        # Call content_query
        engine: SearchEngine = engine.content_query(self.search_term,
                                                    current_page,
                                                    size,
                                                    sort_by=sort_by,
                                                    type_filters=type_filters,
                                                    filter_functions=filter_functions)

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