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

    async def recommend_query(self, page_uri: str, user_id: str=None):
        """
        Executes a query which returns documents similar to the given page uri.
        If user_is is specified, and the user exists, then the users session vector
        is used in conjunction with the page embedding vector for more personalised results.
        :param page_uri:
        :param user_id:
        :raise NotFound: Page with uri page_uri does not exist.
        :return:
        """
        import numpy as np
        from sanic.exceptions import NotFound

        from core.word_embedding.utils import decode_float_list

        from ons.search.response import ONSResponse
        from ons.search.fields import embedding_vector
        from ons.search.conceptual.queries import recommended_content_query

        # First, execute the page_uri query
        s: ConceptualSearchEngine = self._clone()
        s: ConceptualSearchEngine = s.search_by_uri(page_uri)
        response: ONSResponse = await s.execute()

        if response.hits.total > 0:
            json_data = response.hits_to_json()
            documents: list = json_data.get('results', [])
            document = documents[0]

            doc_vector = document.get(embedding_vector.name)

            # Decode the vector
            decoded_doc_vector = np.array(decode_float_list(doc_vector))
            user_vector = None

            # No longer need search engine instance
            del s

            # Add user vector?
            if user_id is not None:
                from core.users.user import User

                user = await User.find_by_user_id(user_id)
                if user is not None:
                    # Get the user vector
                    user_vector = await user.get_user_vector()

            # Build the query
            query = recommended_content_query(
                page_uri, decoded_doc_vector, user_vector=user_vector)
            return self.query(query)
        raise NotFound("No document found with uri '%s'" % page_uri)
