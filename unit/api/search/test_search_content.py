"""
Tests the ONS content search API
"""
from json import dumps
from unit.utils.test_app import TestApp

from api.search.list_type import ListType

from search.search_type import SearchType

from ons.search.index import Index
from ons.search.sort_fields import query_sort, SortField
from ons.search.queries import content_query


class SearchContentApiTestCase(TestApp):

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

    @property
    def search_term(self):
        """
        Mock search term to be used for testing
        :return:
        """
        return "Zuul"

    def test_content_query_search_called(self):
        """
        Tests that the search method is called properly by the api for a content query
        :return:
        """
        # Make the request
        # Set pagination params
        from_start, current_page, size = self.paginate()

        # Set sort_by
        sort_by: SortField = SortField.relevance

        # Build params dict
        params = {
            "q": self.search_term,
            "page": current_page,
            "size": size
        }

        # Build post JSON
        data = {
            "sort_by": sort_by.name
        }

        # URL encode
        url_encoded_params = self.url_encode(params)

        # Loop over list types
        list_type: ListType
        for list_type in ListType:
            target = "/search/{list_type}/content?{q}".format(list_type=list_type.name.lower(), q=url_encoded_params)

            # Make the request
            request, response = self.post(target, 200, data=dumps(data))

            # Build the filter query
            type_filters = list_type.to_type_filters()
            content_type_filters = []
            for type_filter in type_filters:
                for content_type in type_filter.get_content_types():
                    content_type_filters.append(content_type.name)
            filter_query = [
                {
                    "terms": {
                        "type": content_type_filters
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
                            content_query(self.search_term).to_dict(),
                        ]
                    }
                },
                "size": size,
                "sort": query_sort(SortField.relevance)
            }

            # Assert search was called with correct arguments
            self.mock_client.search.assert_called_with(index=[Index.ONS.value], doc_type=[], body=expected,
                                                       search_type=SearchType.DFS_QUERY_THEN_FETCH.value)
