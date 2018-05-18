from server.search.search_engine import SearchEngine


class ConceptualSearchEngine(SearchEngine):
    from server.word_embedding.supervised_models import SupervisedModels, load_model
    word_embedding_model = load_model(SupervisedModels.ONS)

    def __init__(self, *args, **kwargs):
        super(ConceptualSearchEngine, self).__init__(*args, **kwargs)

    async def execute(self, ignore_cache=False):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.

        :arg response_class: optional subclass of ``Response`` to use instead.
        :param ignore_cache: optional argument to ignore response cache and re-execute the query
        """
        import inspect
        from elasticsearch_dsl.connections import connections
        from server.search.fields import embedding_vector

        if ignore_cache or not hasattr(self, '_response'):
            es = connections.get_connection(self._using)
            body = self.to_dict()
            body["_source"] = {
                "excludes": [embedding_vector.name]
            }
            response = es.search(
                index=self._index,
                doc_type=self._doc_type,
                body=body,
                **self._params
            )

            if inspect.isawaitable(response):
                response = await response

            self._response = self._response_class(
                self,
                response
            )

        return self._response

    def content_query(
            self,
            search_term: str,
            current_page: int = 1,
            size: int = 10,
            **kwargs):
        """
        This is the only function we have to overwrite from SearchEngine!
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """
        from .conceptual_search_queries import word_vector_function_score

        query = word_vector_function_score(search_term, ConceptualSearchEngine.word_embedding_model)
        # Prepare and execute
        return self.build_query(
            query,
            current_page=current_page,
            size=size,
            **kwargs)
