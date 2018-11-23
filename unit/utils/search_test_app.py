"""
Test class for Sanic app
"""
from dp4py_sanic.unit.test_app import TestApp

from dp_conceptual_search.app.app import create_app
from dp_conceptual_search.app.search_app import SearchApp


class SearchTestApp(TestApp):

    def get_app(self) -> SearchApp:
        return create_app()

    @property
    def mock_client(self):
        """
        Returns a handle on the mock client object
        :return:
        """
        return self.app.elasticsearch.client
