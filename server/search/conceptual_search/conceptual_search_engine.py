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

    def build_query(self, query: dict, **kwargs):
        from server.search.fields import embedding_vector
        from server.search.conceptual_search.conceptual_search_queries import Scripts, ScriptLanguage

        if "search_term" in kwargs:
            search_term = kwargs.pop("search_term")
            window_size = kwargs.pop("window_size", 100)
            score_mode = kwargs.pop("score_mode", "multiply")

            wv = ConceptualSearchEngine.word_embedding_model.get_sentence_vector(
                search_term)

            params = {
                "cosine": True,
                "field": embedding_vector.name,
                "vector": wv.tolist()
            }
            script_score = {
                "lang": ScriptLanguage.KNN.value,
                "params": params,
                "script": Scripts.BINARY_VECTOR_SCORE.value
            }

            rescore_query_dict = {
                "query": query,
                "rescore": {
                    "window_size": window_size,
                    "query": {
                        "score_mode": score_mode,
                        "rescore_query": {
                            "function_score": {
                                "script_score": script_score
                            }
                        },
                        "query_weight": 0.0,
                        "rescore_query_weight": 1.0
                    }
                }
            }
            return super(
                ConceptualSearchEngine,
                self).build_query(
                rescore_query_dict,
                **kwargs)

        return super(ConceptualSearchEngine, self).build_query(query, **kwargs)

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
        from .conceptual_search_queries import content_query

        # TODO - test with/without script scoring
        query = content_query(
            search_term, ConceptualSearchEngine.word_embedding_model)
        # Prepare and execute
        query_dict = query.to_dict()
        return self.build_query(
            query_dict,
            search_term=search_term,
            current_page=current_page,
            size=size,
            **kwargs)

    def featured_result_query(self, search_term):
        """
        Builds and executes the standard ONS featured result query (from babbage)
        :param search_term:
        :return:
        """
        return super(ConceptualSearchEngine,
                     self).featured_result_query(search_term)
