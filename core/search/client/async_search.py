from elasticsearch_dsl import Search

from core.search.search_type import SearchType


class AsyncSearch(Search):
    """
    A search client which supports async http calls
    """
    @property
    def query_size(self):
        return self.to_dict().get("size", 0)

    def search_type(self, search_type: SearchType):
        """
        Adds search_type param to Elasticsearch query
        :param search_type:
        :return:
        """

        return self.params(search_type=search_type.value)

    async def execute(self, ignore_cache=False):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.
        :arg response_class: optional subclass of ``Response`` to use instead.
        :param ignore_cache: optional argument to ignore response cache and re-execute the query
        """
        import inspect
        from elasticsearch_dsl.connections import connections

        if ignore_cache or not hasattr(self, '_response'):
            es = connections.get_connection(self._using)
            response = es.search(
                index=self._index,
                doc_type=self._doc_type,
                body=self.to_dict(),
                **self._params
            )

            if inspect.isawaitable(response):
                response = await response

            self._response = self._response_class(
                self,
                response
            )

        return self._response
