"""
Defines the search engine for recommendation queries
"""
from numpy import ndarray

from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.recommend.queries.ons_query_builders import similar_to_uri
from dp_conceptual_search.ons.conceptual.client.conceptual_search_engine import ConceptualSearchEngine


class RecommendationSearchEngine(ConceptualSearchEngine):

    async def similar_by_uri_query(self, uri: str, num_labels, page: int, page_size: int,
                                   sort_by: SortField = SortField.relevance, **kwargs):
        """
        Queries for content similar to (but excluding) the given uri
        :param uri:
        :param num_labels:
        :param page:
        :param page_size:
        :param sort_by:
        :return:
        """
        # Get the page embedding vector
        embedding_vector: ndarray = await self.embedding_vector_for_uri(uri)

        # Generate the keywords
        keywords = await self.similar_by_vector(embedding_vector, num_labels, **kwargs)

        # Build the query
        vector_script: VectorScriptScore = self.vector_script_score(embedding_vector)
        query: Q.Query = similar_to_uri(uri, keywords, vector_script)

        s: RecommendationSearchEngine = self._clone()

        # Paginate
        s: RecommendationSearchEngine = s.paginate(page, page_size)

        # Sort
        s: RecommendationSearchEngine = s.sort_by(sort_by)

        # Set query
        s: RecommendationSearchEngine = s.query(query)

        # Execute and return
        return s
