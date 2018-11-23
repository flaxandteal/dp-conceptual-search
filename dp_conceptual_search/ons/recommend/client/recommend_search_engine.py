"""
Defines the search engine for recommendation queries
"""
from numpy import ndarray

from elasticsearch_dsl import query as Q

from dp_conceptual_search.search.search_type import SearchType
from dp_conceptual_search.search.dsl.vector_script_score import VectorScriptScore

from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.recommend.queries.ons_query_builders import similar_to_uri
from dp_conceptual_search.ons.conceptual.client.conceptual_search_engine import ConceptualSearchEngine


class RecommendationSearchEngine(ConceptualSearchEngine):

    async def similar_by_uri_query(self, uri: str, num_labels, page: int, page_size: int,
                                   sort_by: SortField = SortField.relevance,
                                   highlight: bool=True,
                                   **kwargs):
        """
        Queries for content similar to (but excluding) the given uri
        :param uri:
        :param num_labels:
        :param page:
        :param page_size:
        :param sort_by:
        :param highlight:
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

        # Set query
        s: RecommendationSearchEngine = s.query(query) \
            .paginate(page, page_size) \
            .search_type(SearchType.DFS_QUERY_THEN_FETCH) \
            .sort_by(sort_by)

        if highlight:
            s: RecommendationSearchEngine = s.apply_highlight_fields()

        # Execute and return
        return s
