from elasticsearch_dsl import Search


class SearchClient(Search):
    """
    Class to re-work the execute method to allow better inheritance
    """
    def __init__(self, *args, **kwargs):
        super(SearchClient, self).__init__(*args, **kwargs)
        from elasticsearch_dsl.response import Response

        # Define response object
        self._response = None

        # Define response class object
        response_cls = kwargs.get("response_class", Response)
        self._response_class = response_cls

    def _get_elasticsearch_client(self):
        """
        Return a living connection to the underlying Elasticsearch client
        :return:
        """
        from elasticsearch_dsl.connections import connections
        es = connections.get_connection(self._using)

        return es

    async def _search(self):
        """
        Execute the search request and return the raw response
        If the response is a co-routine, then await it
        :return:
        """
        from inspect import isawaitable

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

    async def execute(self, ignore_cache=False):
        """
        Wraps the Elasticsearch response in the given response class
        :param ignore_cache:
        :return:
        """
        if ignore_cache or not hasattr(self, '_response'):
            search_response = await self._search()

            self._response = self._response_class(self, search_response)

        return self._response
