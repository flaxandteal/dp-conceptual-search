import abc
import os

from elasticsearch_dsl import Search

from server.search.search_type import SearchType
from server.search.sort_by import SortFields


_INDEX = os.environ.get('SEARCH_INDEX', 'ons*')


def get_index():
    return _INDEX


class BaseSearchEngine(abc.ABC, Search):
    def __init__(self, **kwargs):
        super(BaseSearchEngine, self).__init__(**kwargs)

    @property
    def query_size(self):
        return self.to_dict().get("size", 0)

    def highlight_fields(self):
        """
        Appends highligher options onto Elasticsearch query
        :return:
        """
        from server.search.fields import highlight_fields

        field_names = [field.name for field in highlight_fields]

        return self.highlight(
            *field_names,
            fragment_size=0,
            pre_tags=["<strong>"],
            post_tags=["</strong>"])

    def search_type(self, search_type: SearchType):
        """
        Adds search_type param to Elasticsearch query
        :param search_type:
        :return:
        """

        return self.params(search_type=search_type.value)

    def sort_by(self, sort_by: SortFields):
        """
        Adds sort options to query
        :param sort_by:
        :return:
        """
        from server.search.sort_by import query_sort

        return self.sort(
            *query_sort(sort_by)
        )

    def type_filter(self, type_filters):

        if not isinstance(type_filters, list):
            type_filters = [type_filters]

        return self.filter("terms", type=type_filters)

    def build_query(self, query: dict, **kwargs):
        if "query" not in query:
            query = {
                "query": query
            }

        if "aggs" in kwargs:
            query["aggs"] = kwargs.pop("aggs")

        if "current_page" in kwargs and "size" in kwargs:
            current_page = kwargs.pop("current_page")
            size = kwargs.pop("size")

            from_start = 0 if current_page <= 1 else (current_page - 1) * size

            query["from"] = from_start
            query["size"] = size

        # Update query from dict
        self.update_from_dict(query)

        s = self._clone()

        # Add type filters?
        type_filters = kwargs.get("type_filters", None)

        if type_filters is not None:
            s = s.type_filter(type_filters)

        # Highlight
        s = s.highlight_fields()

        # Sort
        if "sort_by" in kwargs:
            sort_by = kwargs.pop("sort_by")
            s = s.sort_by(sort_by)

        # Set search type
        search_type = kwargs.get(
            "search_type",
            SearchType.DFS_QUERY_THEN_FETCH)
        s = s.search_type(search_type)

        return s

    async def execute(self, ignore_cache=False):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.

        :arg response_class: optional subclass of ``Response`` to use instead.
        :param ignore_cache: optional argument to ignore response cache and re-execute the query
        """
        import inspect
        from elasticsearch_dsl.connections import connections

        if ignore_cache or not hasattr(self, '_response'):
            es = connections.get_connection(self._using)
            response = es.search(
                index=self._index,
                doc_type=self._doc_type,
                body=self.to_dict(),
                **self._params
            )

            if inspect.isawaitable(response):
                response = await response

            self._response = self._response_class(
                self,
                response
            )

        return self._response

    @abc.abstractmethod
    def content_query(
            self,
            search_term: str,
            current_page: int = 1,
            size: int = 10,
            **kwargs):
        pass

    @abc.abstractmethod
    def type_counts_query(self, search_term, **kwargs):
        pass

    @abc.abstractmethod
    def featured_result_query(self, search_term):
        pass


class SearchEngine(BaseSearchEngine):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)

    def content_query(
            self,
            search_term: str,
            current_page: int = 1,
            size: int = 10,
            **kwargs):
        """
        Builds and executes the standard ONS content query (from babbage)
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """
        from server.search.queries import content_query, function_score_content_query
        from .filter_functions import content_filter_functions

        function_scores = kwargs.pop(
            "function_scores", content_filter_functions())

        # Build the standard content query
        query = content_query(search_term)

        if function_scores is not None:
            query = function_score_content_query(
                query,
                function_scores)

        # Prepare and execute
        query_dict = query.to_dict()
        return self.build_query(
            query_dict,
            current_page=current_page,
            size=size,
            **kwargs)

    def type_counts_query(self, search_term, **kwargs):
        from .type_filter import all_filter_funcs
        from server.search.queries import type_counts_query

        # Prepare and execute
        return self.content_query(
            search_term,
            function_scores=None,
            aggs=type_counts_query,
            type_filters=all_filter_funcs(),
            **kwargs)

    def featured_result_query(self, search_term):
        """
        Builds and executes the standard ONS featured result query (from babbage)
        :param search_term:
        :return:
        """
        from .content_types import home_page_census, product_page

        type_filters = [product_page.name, home_page_census.name]

        s = self.content_query(
            search_term,
            function_scores=None,
            type_filters=type_filters,
            size=1)
        return s
