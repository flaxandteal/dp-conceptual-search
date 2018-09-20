"""
Tests that the ONSRequest properly parses input params
"""
from unit.utils.test_app import TestApp
from unit.ons.search.search_test_case import SearchTestCase

from core.search.search_type import SearchType

from ons.search.index import Index
from ons.search.sort_fields import SortField
from ons.search.queries import content_query


class ONSRequestTestCase(TestApp, SearchTestCase):

    def assert_sort_by(self, sort_by: SortField):
        """
        Assert search was called with correct sort option
        :param sort_by:
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
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

    def test_sort_by_relevance(self):
        """
        Tests that the search method is called properly by the server for a content query
        :return:
        """
        self.assert_sort_by(SortField.relevance)

    # def test_sort_by_release_date(self):
    #     """
    #     Tests that the search method is called properly by the server for a content query
    #     :return:
    #     """
    #     self.assert_sort_by(SortField.release_date)
