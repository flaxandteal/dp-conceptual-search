from server.search.search_engine import SearchEngine


class ConceptualSearchEngine(SearchEngine):
    from server.word_embedding.supervised_models import SupervisedModels, load_model
    word_embedding_model = load_model(SupervisedModels.ONS)

    def __init__(self, *args, **kwargs):
        super(ConceptualSearchEngine, self).__init__(*args, **kwargs)

    def build_query(self, query: dict, **kwargs):
        from server.search.fields import embedding_vector
        from server.search.conceptual_search.conceptual_search_queries import Scripts, ScriptLanguage

        if "search_term" in kwargs:
            search_term = kwargs.pop("search_term")
            window_size = kwargs.pop("window_size", 100)
            score_mode = kwargs.pop("score_mode", "max")
            query_weight = kwargs.pop("query_weight", 1.0)
            rescore_query_weight = kwargs.pop("rescore_query_weight", 10.0)

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
                                "boost_mode": "replace",
                                "script_score": script_score
                            }
                        },
                        "query_weight": query_weight,
                        "rescore_query_weight": rescore_query_weight
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
        Overwrite SearchEngine content query to use a vector rescore.
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """
        from server.search.fields import embedding_vector
        from server.search.sort_by import SortFields

        from .conceptual_search_queries import content_query

        # We only do this for relevancy sorting
        sort_by = kwargs.pop("sort_by", SortFields.relevance)
        if isinstance(sort_by, SortFields) and sort_by == SortFields.relevance:

            # TODO - test with/without script scoring
            query = content_query(
                search_term, ConceptualSearchEngine.word_embedding_model)
            # Prepare and execute
            query_dict = query.to_dict()

            s = self.build_query(
                query_dict,
                search_term=search_term,
                current_page=current_page,
                size=size,
                **kwargs)

            # Exclude embedding vector for source
            s = s.source(exclude=[embedding_vector.name])
            return s
        else:
            # Execute the regular content query with sorting
            return super(
                ConceptualSearchEngine,
                self).content_query(
                search_term,
                current_page=current_page,
                size=size,
                sort_by=sort_by,
                **kwargs)

    def featured_result_query(self, search_term):
        """
        Builds and executes the standard ONS featured result query (from babbage)
        :param search_term:
        :return:
        """
        return super(ConceptualSearchEngine,
                     self).featured_result_query(search_term)
