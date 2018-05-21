import os
from elasticsearch_dsl import Search as Search_api
from elasticsearch_dsl.connections import connections

from . import fields
from .search_type import SearchType
from .type_filter import all_filter_funcs
from .sort_by import SortFields, query_sort
from .queries import content_query, type_counts_query
from .filter_functions import content_filter_functions
from .content_types import home_page_census, product_page

_INDEX = os.environ.get('SEARCH_INDEX', 'ons*')


def get_index():
    return _INDEX


"""
TODO - Implement MultiSearch:
http://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=multisearch#multisearch
"""


class SearchEngine(Search_api):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)

    def highlight_fields(self):
        """
        Appends highligher options onto Elasticsearch query
        :return:
        """
        s = self._clone()

        field_names = [field.name for field in fields.highlight_fields]

        s = s.highlight(
            *field_names,
            fragment_size=0,
            pre_tags=["<strong>"],
            post_tags=["</strong>"])

        return s

    @staticmethod
    def build_content_query(search_term, **kwargs):
        """
        Builds the default ONS content query (from babbage)
        :param search_term:
        :param kwargs:
        :return:
        """
        function_scores = kwargs.pop(
            "function_scores", content_filter_functions())

        query = {
            "query": content_query(
                search_term,
                function_scores=function_scores).to_dict()}

        if "current_page" in kwargs and "size" in kwargs:
            current_page = kwargs["current_page"]
            size = kwargs["size"]
            from_start = 0 if current_page <= 1 else (current_page - 1) * size

            query["from"] = from_start
            query["size"] = size
        return query

    def _execute_query(self, query, **kwargs):
        """
        Internal function to execute a generic query and process
        additional arguments, such as sort_by and type_filters
        :param query:
        :param kwargs:
        :return:
        """
        # Clone the SearchEngine before we make changes to it
        s = self._clone()

        # Update query from dict
        s.update_from_dict(query)

        # Add type filters?
        type_filters = kwargs.get("type_filters", None)

        if type_filters is not None:
            if isinstance(
                    type_filters,
                    str) or hasattr(
                    type_filters,
                    "__iter__") is False:
                type_filters = [type_filters]
            s = s.filter("terms", type=type_filters)

        # Highlight
        s = s.highlight_fields()

        # Sort
        if "sort_by" in kwargs:
            sort_by = kwargs.pop("sort_by")
            assert isinstance(
                sort_by, SortFields), "sort_by must be instance of SortFields"
            s = s.sort(
                *query_sort(sort_by)
            )

        # DFS_QUERY_THEN_FETCH
        search_type = kwargs.get(
            "search_type",
            SearchType.DFS_QUERY_THEN_FETCH)
        s = s.search_type(search_type)

        return s

    def content_query(
            self,
            search_term,
            current_page=1,
            size=10,
            **kwargs):
        """
        Builds and executes the standard ONS content query (from babbage)
        :param search_term:
        :param current_page:
        :param size:
        :param kwargs:
        :return:
        """

        # Build the standard content query
        query = SearchEngine.build_content_query(
            search_term, current_page=current_page, size=size, **kwargs)

        # Execute
        return self._execute_query(query, **kwargs)

    def type_counts_query(self, search_term):
        """
        Builds and executes the standard ONS types count query (from babbage)
        :param search_term:
        :return:
        """
        # Use all relevant doc_types
        type_filters = all_filter_funcs()

        # Build the standard content query
        query = SearchEngine.build_content_query(search_term)

        # Add aggregations
        query["aggs"] = type_counts_query()

        # Execute
        return self._execute_query(
            query,
            type_filters=type_filters)

    def featured_result_query(self, search_term):
        """
        Builds and executes the standard ONS featured result query (from babbage)
        :param search_term:
        :return:
        """
        # Build the default content query without filter functions
        dis_max = content_query(search_term)
        query = {
            "size": 1,
            "query": dis_max.to_dict()
        }

        # Add doc_type filters
        type_filters = [product_page.name, home_page_census.name]

        # Execute the query
        return self._execute_query(query, type_filters=type_filters)

    def search_type(self, search_type):
        """
        Adds search_type param to Elasticsearch query
        :param search_type:
        :return:
        """
        assert isinstance(
            search_type, SearchType), "Must supply instance of SearchType enum"
        s = self._clone()
        s = s.params(search_type=search_type)

        return s

    async def execute(self, ignore_cache=False):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.

        :arg response_class: optional subclass of ``Response`` to use instead.
        :param ignore_cache: optional argument to ignore response cache and re-execute the query
        """
        import inspect

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
