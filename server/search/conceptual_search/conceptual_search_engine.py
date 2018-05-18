from server.search.search_engine import SearchEngine


class ConceptualSearchEngine(SearchEngine):
    from server.word_embedding.supervised_models import SupervisedModels, load_model
    word_embedding_model = load_model(SupervisedModels.ONS)

    def __init__(self, *args, **kwargs):
        super(ConceptualSearchEngine, self).__init__(*args, **kwargs)

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
        raise NotImplementedError("Conceptual search not yet implemented")
