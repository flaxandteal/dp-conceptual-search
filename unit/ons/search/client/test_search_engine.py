from core.search.client.search_client import SearchClient
from ons.search.client.search_engine import SearchEngine

from unit.utils.elasticsearch_test_case import ElasticsearchTestCase


class SearchEngineTestCase(ElasticsearchTestCase):
    """
    Unit test for ONS SearchEngine class

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
                    "name": "Randy Marsh"
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

    def get_search_engine(self) -> SearchEngine:
        """
        Create an instance of a SearchEngine for testing
        :return:
        """
        engine = SearchEngine(using=self.mock_client, index=self.index)
        return engine

    def paginate(self, engine: SearchEngine):
        """
        Calls paginate and makes some basic assertions
        :return:
        """
        import random

        # Generate a random page number between 1 and 10
        current_page = random.randint(1, 10)

        # Generate a random page size between 11 and 20
        size = random.randint(11, 20)

        # Call paginate
        engine: SearchEngine = engine.paginate(current_page, size)

        # Calculate correct start page number
        from_start = 0 if current_page <= 1 else (current_page - 1) * size

        # Convert to dictionary
        engine_dict = engine.to_dict()
        self.assertIsNotNone(engine_dict, "engine dict should not be none")

        return from_start, current_page, size, engine

    def assertEqualDicts(self, first: dict, second: dict):
        """
        Asserts two dics are equal without requiring same ordering
        :param first:
        :param second:
        :param msg:
        :return:
        """
        for key in first:
            self.assertIn(key, second, "key '{0}' should exist in engine dict".format(key))
            self.assertEqual(first[key], second[key],
                             "value for key '{0}' should match expected value".format(key))

    def test_sort_by(self):
        """
        Test that sort_by works as expected
        :return:
        """
        from ons.search.sort_fields import query_sort, SortFields

        # Loop over all possible sort options
        for sort_by in SortFields:
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
        from_start, current_page, size, engine = self.paginate(engine)

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

        self.assertEqualDicts(expected, engine_dict)

    def test_departments_query(self):
        """
        Test that departments query calls search on SearchClient correctly
        :return:
        """
        import asyncio

        # Create instance of SearchEngine
        engine = self.get_search_engine()

        # Paginate
        from_start, current_page, size, engine = self.paginate(engine)

        # Generate expected query
        search_term = "Who ya gonna call?"
        expected = {
            "from": from_start,
            "query": {
                "match": {
                    "terms": {
                        "query": search_term,
                        "type": "boolean"
                    }
                }
            },
            "size": size
        }

        # Call departments_query
        engine: SearchEngine = engine.departments_query(search_term, current_page, size)

        # Assert correct dict structure
        engine_dict = engine.to_dict()
        self.assertEqualDicts(expected, engine_dict)

        # Call execute asynchronously and test method calls
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_async():
            from core.search.search_type import SearchType
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=engine_dict,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()
