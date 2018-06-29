from ons.search.search_engine import SearchEngine
from ons.search.sort_fields import SortFields

from numpy import ndarray


class ConceptualSearchEngine(SearchEngine):
    from server.word_embedding.sanic_supervised_models import load_model
    from core.word_embedding.models.supervised import SupervisedModels, SupervisedModel

    user_vector_key = "user_vector"
    word_embedding_model: SupervisedModel = load_model(SupervisedModels.ONS)

    def content_query(
            self,
            search_term: str,
            current_page: int = 1,
            size: int = 10,
            sort_by: SortFields=SortFields.relevance,
            **kwargs):
        """
        Overwrite SearchEngine content query to use a vector rescore.
        :param search_term:
        :param current_page:
        :param size:
        :param sort_by:
        :param kwargs:
        :return:
        """
        from ons.search.fields import embedding_vector
        from ons.search.sort_fields import SortFields
        from ons.search.conceptual.queries import content_query

        if sort_by == SortFields.relevance:
            # Build the content query with vector function score
            query = content_query(
                search_term,
                ConceptualSearchEngine.word_embedding_model,
                **kwargs)

            # Build the query
            s: ConceptualSearchEngine = self.build(
                query,
                search_term=search_term,
                current_page=current_page,
                size=size,
                sort_by=None,  # None to prevent sorting from influencing scores
                **kwargs)

            # Setup pagination
            s: ConceptualSearchEngine = s.paginate(current_page, size)

            # Add the rescore?
            # If user_vector is specified, add a user vector function score
            if self.user_vector_key in kwargs:
                from ons.search.conceptual.queries import user_rescore_query

                user_vector: ndarray = kwargs.get(self.user_vector_key)

                if user_vector is not None and isinstance(
                        user_vector, ndarray):

                    rescore = user_rescore_query(user_vector)
                    s: ConceptualSearchEngine = s.extra(**rescore.to_dict())

            # Exclude embedding vector for source
            s: ConceptualSearchEngine = s.source(
                exclude=[embedding_vector.name])

            return s
        else:
            return super(
                ConceptualSearchEngine,
                self).content_query(
                search_term,
                current_page=current_page,
                size=size,
                **kwargs)

    def featured_result_query(self, search_term):
        """
        Builds and executes the standard ONS featured result query (from babbage)
        :param search_term:
        :return:
        """
        from ons.search.content_type import home_page_census, product_page

        type_filters = [product_page.name, home_page_census.name]

        s = super(ConceptualSearchEngine,
                  self).content_query(
            search_term,
            function_scores=None,
            type_filters=type_filters,
            size=1)
        return s
