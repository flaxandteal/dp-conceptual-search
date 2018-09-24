"""
Unit tests for search route
"""
from json import dumps

from unit.utils.test_app import TestApp
from unit.ons.search.search_test_case import SearchTestCase

from search.search_type import SearchType

from ons.search.index import Index
from ons.search.sort_fields import SortField
from ons.search.queries import content_query, departments_query


class SearchTestCase(TestApp, SearchTestCase):

    def test_proxy_api_raises_400(self):
        """
        Tests that the proxy search API raises a 400 when no query body is specified (or the 'query' key doesn't exist)
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        params = {
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/?{0}".format(url_encoded_params)

        # Make the request
        request, response = self.post(target, 400)

        # Specify data but with no query key
        # Build expected query
        # Build the content query and convert to dict
        query = {
            "query" : {
                "match": {
                    "name": "Zuul"
                }
            }
        }

        post_params = {
            "wrong_key": dumps(query)
        }
        # Make the request
        request, response = self.post(target, 400, data=dumps(post_params))

    def test_proxy_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a proxy query
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        params = {
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/?{0}".format(url_encoded_params)

        # Build expected query
        # Build the content query and convert to dict
        query = {
            "query" : {
                "match": {
                    "name": "Zuul"
                }
            }
        }

        post_params = {
            "query": dumps(query)
        }

        # Make the request
        request, response = self.post(target, 200, data=dumps(post_params))

        # Build the expected query dict - note this should not change
        expected = query

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected)

    def test_departments_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a departments query
        :return:
        """
        # Make the request
        from_start, current_page, size = self.paginate()
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size
        }
        url_encoded_params = self.url_encode(params)
        target = "/search/ons/departments?{0}".format(url_encoded_params)

        # Make the request
        request, response = self.get(target, 200)

        # Build expected query
        # Build the content query and convert to dict
        query = departments_query(self.search_term)

        # Get the resulting query dict
        query_dict = query.to_dict()

        # Build the expected query dict - note this should not change
        expected = self.expected_departments_query(from_start, size, query_dict)

        # Assert search was called with correct arguments
        self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                   search_type=SearchType.DFS_QUERY_THEN_FETCH.value)

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
