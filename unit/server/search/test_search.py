"""
Unit tests for search route
"""
from unit.utils.test_app import TestApp
from unit.ons.search.test_utils import SearchTestUtils


class SearchTestCase(TestApp, SearchTestUtils):

    def test_content_query_search_called(self):
        """
        Tests that the search method is called properly by the server for a content query
        :return:
        """
        from core.search.search_type import SearchType

        from ons.search.index import Index
        from ons.search.queries import content_query

        # Make the request
        from_start, current_page, size = self.paginate()
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/ons/content?{0}".format(url_encoded_params)

        # Make the request
        request, response = self.get(target, 200)

        # Build expected query
        # Build the content query and convert to dict
        query = content_query(self.search_term)

        # Get the resulting query dict
        query_dict = query.to_dict()

        # Build the expected query dict - note this should not change
        expected = self.expected_content_query(from_start, size, query_dict)

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

    def test_type_counts_query_search_called(self):
        """
        Tests that the search method is called properly by the server for a type counts query
        :return:
        """
        from core.search.search_type import SearchType

        from ons.search.index import Index
        from ons.search.queries import content_query

        # Make the request
        params = {
            "q": self.search_term
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/ons/counts?{0}".format(url_encoded_params)

        # Make the request
        request, response = self.get(target, 200)

        # Build expected query
        # Build the content query and convert to dict
        query = content_query(self.search_term)

        # Get the resulting query dict
        query_dict = query.to_dict()

        # Build the expected query dict - note this should not change
        expected = self.expected_type_counts_query(query_dict)

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)
