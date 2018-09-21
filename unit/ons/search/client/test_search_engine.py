from ons.search.sort_fields import SortField
from ons.search.client.search_engine import SearchEngine

from unit.ons.search.search_test_case import SearchTestCase


class SearchEngineTestCase(SearchTestCase):
    """
    Unit test for ONS SearchEngine class

    """

    def test_sort_by(self):
        """
        Test that sort_by works as expected
        :return:
        """
        from ons.search.sort_fields import query_sort, SortField

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

        self.assertEqualDicts(expected, engine_dict)

    def test_departments_query(self):
        """
        Test that the departments query calls search on SearchClient correctly
        :return:
        """
        import asyncio

        # Create instance of SearchEngine
        engine = self.get_search_engine()

        # Calculate correct start page number
        from_start, current_page, size = self.paginate()

        # Generate expected query

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

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()

    def test_content_query_no_filter_functions(self):
        """
        Test that the content query calls search on SearchClient correctly with no filter functions
        :return:
        """
        import asyncio

        # Setup content query with no type filters
        sort_by: SortField = SortField.relevance
        engine, expected = self.setUpContentQuery(sort_by)

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

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()

    def test_content_query_with_filter_functions(self):
        """
        Test that the content query calls search on SearchClient correctly with filter functions
        :return:
        """
        import asyncio
        from ons.search.content_type import ContentTypes

        # Setup content type filters
        filter_by_content_types = [
            ContentTypes.BULLETIN.value,
            ContentTypes.ARTICLE.value
        ]

        # Setup content query with type filters
        sort_by: SortField = SortField.relevance
        engine, expected = self.setUpContentQuery(sort_by, filter_by_content_types=filter_by_content_types)

        # Call execute asynchronously and test method calls
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_async():
            from core.search.search_type import SearchType
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()

    def test_type_counts_query(self):
        """
        Test that the type counts query calls search on SearchClient correctly
        :return:
        """
        import asyncio

        from ons.search.queries import content_query
        from ons.search.paginator import RESULTS_PER_PAGE

        # Create instance of SearchEngine
        engine = self.get_search_engine()

        # Build expected query body
        query = content_query(self.search_term)
        query_dict = query.to_dict()

        from_start = SearchEngine.default_page_number - 1
        sort_by: SortField = SortField.relevance
        expected = self.expected_content_query(from_start, RESULTS_PER_PAGE, query_dict, sort_by)

        # Add aggregations body
        expected["aggs"] = {
            "docCounts": {
                "terms": {
                    "field": "_type"
                }
            }
        }

        # Call type_counts_query
        engine: SearchEngine = engine.type_counts_query(self.search_term)

        # Call execute asynchronously and test method calls
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_async():
            from core.search.search_type import SearchType
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()

    def test_featured_results_query(self):
        """
        Test that the featured results query calls search on SearchClient correctly
        :return:
        """
        import asyncio

        from ons.search.queries import content_query

        # Create instance of SearchEngine
        engine = self.get_search_engine()

        # Build expected query body
        query = content_query(self.search_term)
        query_dict = query.to_dict()

        expected = self.expected_featured_result_query(query_dict)

        # Call featured_result_query
        engine: SearchEngine = engine.featured_result_query(self.search_term)

        # Call execute asynchronously and test method calls
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_async():
            from core.search.search_type import SearchType
            # Ensure search method on SearchClient is called correctly on execute
            response = await engine.execute(ignore_cache=True)

            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()