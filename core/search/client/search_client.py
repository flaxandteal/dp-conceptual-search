from inspect import isawaitable

from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response
from elasticsearch_dsl.connections import connections

from core.search.search_type import SearchType


class SearchClient(Search):
    """
    Class to re-work the execute method to allow better inheritance
    """
    def __init__(self, response_class=Response, **kwargs):
        """
        Initialise the SearchClient responsible for sending requests to Elasticsearch
        :param response_class: Class to wrap Elasticsearch response
        :param kwargs: Additional arguments for elasticsearch_dsl.Search client
        """
        super(SearchClient, self).__init__(**kwargs)
        # Define response object
        self._response = None

        # Define response class object
        self._response_class = response_class

    def _get_elasticsearch_client(self):
        """
        Return a living connection to the underlying Elasticsearch client
        :return:
        """
        es = connections.get_connection(self._using)

        return es

    async def _search(self):
        """
        Execute the search request and return the raw response
        If the response is a co-routine, then await it
        :return:
        """
        es = self._get_elasticsearch_client()

        response = es.search(
            index=self._index,
            doc_type=self._get_doc_type(),
            body=self.to_dict(),
            **self._params
        )

        if isawaitable(response):
            response = await response
        return response

    def search_type(self, search_type: SearchType):
        """
        Adds search_type param to Elasticsearch query
        :param search_type:
        :return:
        """
        return self.params(search_type=search_type.value)

    async def execute(self, ignore_cache=False):
        """
        Wraps the Elasticsearch response in the given response class
        :param ignore_cache:
        :return:
        """
        if ignore_cache or not hasattr(self, '_response') or self._response is None:
            search_response = await self._search()

            self._response = self._response_class(self, search_response)

        return self._response
