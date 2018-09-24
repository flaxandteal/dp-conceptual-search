"""
Tests the ONSResponse class
"""
from unit.ons.search.search_test_case import SearchTestCase

from ons.search.response.search_result import SearchResult
from ons.search.response.client.ons_response import ONSResponse
from ons.search.client.search_engine import SearchEngine


class ONSResponseTestCase(SearchTestCase):

    def test_ons_response(self):
        """
        Tests that the ONSResponse class properly interfaces with the elasticsearch_dsl.response.Response class
        and unmarshalls the JSON to a valid SearchResult
        :return:
        """
        import asyncio
        from ons.search.sort_fields import SortField

        engine: SearchEngine = self.get_search_engine()

        # Use the departments method to trigger the query execution
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

        # Call execute asynchronously and test method calls
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        async def run_async():
            from ons.search.paginator import Paginator
            from search.search_type import SearchType
            from ons.search.response.content_query_result import ContentQueryResult

            # Ensure search method on SearchClient is called correctly on execute
            response: ONSResponse = await engine.execute(ignore_cache=True)

            # Check call was made correctly
            self.mock_client.search.assert_called_with(index=[self.index], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

            # Make some assertions about the response object
            self.assertIsInstance(response, ONSResponse, "response should be instance of ONSResponse")

            # Attempt to build SearchResult
            sort_by = SortField.relevance
            result: SearchResult = response.to_content_query_search_result(current_page, size, sort_by)

            self.assertIsNotNone(result, "result should not be none")
            self.assertIsInstance(result, SearchResult,
                                  "result should be instance of ons.search.response.search_result.SearchResult")

            # Build the expected SearchResult
            hits = [hit["_source"] for hit in self.mock_hits]
            num_hits = len(hits)
            took = self.mock_took

            paginator = Paginator(
                num_hits,
                current_page,
                result_per_page=size
            )

            expected_result: ContentQueryResult = ContentQueryResult(
                num_hits,
                took,
                hits,
                paginator,
                sort_by
            )

            result_dict = result.to_dict()
            expected_result_dict = expected_result.to_dict()

            # Assert they're the same
            self.assertEqualDicts(result_dict, expected_result_dict)

        # Run the async test
        coro = asyncio.coroutine(run_async)
        event_loop.run_until_complete(coro())
        event_loop.close()



