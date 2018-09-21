"""
Unit tests for search route
"""
from unit.utils.test_app import TestApp
from unit.ons.search.search_test_case import SearchTestCase

from search.search_type import SearchType

from ons.search.index import Index
from ons.search.sort_fields import SortField
from ons.search.queries import content_query


class SearchTestCase(TestApp, SearchTestCase):

    def test_content_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a content query
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        sort_by: SortField = SortField.relevance
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size,
            "sort_by": sort_by.name
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
        expected = self.expected_content_query(from_start, size, query_dict, sort_by)

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

    def test_type_counts_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a type counts query
        :return:
        """
        # Make the request
        sort_by: SortField = SortField.relevance
        params = {
            "q": self.search_term,
            "sort_by": sort_by.name
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
        expected = self.expected_type_counts_query(query_dict, sort_by)

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

    def test_featured_result_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a featured result query
        :return:
        """
        # Make the request
        params = {
            "q": self.search_term
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/ons/featured?{0}".format(url_encoded_params)

        # Make the request
        request, response = self.get(target, 200)

        # Build expected query
        # Build the content query and convert to dict
        query = content_query(self.search_term)

        # Get the resulting query dict
        query_dict = query.to_dict()

        # Build the expected query dict - note this should not change
        expected = self.expected_featured_result_query(query_dict)

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)
