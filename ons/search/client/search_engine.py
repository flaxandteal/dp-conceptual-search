from ons.search.client.abstract_search_engine import AbstractSearchEngine


class SearchEngine(AbstractSearchEngine):
    """
    Implementation of the ONS search engine
    """

    def departments_query(self, search_term: str, current_page: int, size: int):
        from core.search.search_type import SearchType
        from ons.search.queries import departments_query

        s: SearchEngine = self._clone()\
            .query(departments_query(search_term))\
            .paginate(current_page, size)\
            .search_type(SearchType.DFS_QUERY_THEN_FETCH)

        return s

    def content_query(self, search_term: str, current_page: int = 1, size: int = 10, **kwargs):
        pass

    def type_counts_query(self, search_term, **kwargs):
        pass

    def featured_result_query(self, search_term):
        pass
