import inspect

from elasticsearch_dsl import MultiSearch
from elasticsearch_dsl.response import Response

from elasticsearch.exceptions import TransportError


class AsyncMultiSearch(MultiSearch):
    def __init__(self, *args, **kwargs):
        super(AsyncMultiSearch, self).__init__(*args, **kwargs)

    async def execute(self, ignore_cache=False, raise_on_error=True):
        """
        Execute the multi search request and return a list of search results.
        """
        from elasticsearch_dsl.connections import connections

        if ignore_cache or not hasattr(self, '_response'):
            es = connections.get_connection(self._using)

            responses = es.msearch(
                index=self._index,
                doc_type=self._get_doc_type(),
                body=self.to_dict(),
                **self._params
            )

            if inspect.isawaitable(responses):
                responses = await responses

            out = []
            for s, r in zip(self._searches, responses['responses']):
                if r.get('error', False):
                    if raise_on_error:
                        raise TransportError(
                            'N/A', r['error']['type'], r['error'])
                    r = None
                else:
                    r = Response(s, r)
                out.append(r)

            self._response = out

        return self._response
