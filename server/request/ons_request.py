from sanic.request import Request
from sanic.exceptions import InvalidUsage

from ons.search.sort_fields import SortFields
from ons.search.paginator import RESULTS_PER_PAGE

from server.sanic_elasticsearch import SanicElasticsearch


class ONSRequest(Request):
    """
    Custom ONS request class which implements some useful methods for request parsing
    """

    def get_search_term(self) -> str:
        """
        Parses the request to extract a search term
        :return:
        """
        search_term = self.args.get("q", None)
        if search_term is None:
            raise InvalidUsage("Search term not specified")
        return search_term

    def get_current_page(self) -> int:
        """
        Returns the requested page number. Defaults to the first page.
        :return:
        """
        current_page = self.args.get("page", 1)
        return int(current_page)

    def get_page_size(self) -> int:
        """
        Returns the requested page size. Defaults to the value set by the paginator.
        :return:
        """
        page_size = self.args.get("size", RESULTS_PER_PAGE)
        return int(page_size)

    def get_sort_by(self) -> SortFields:
        """
        Returns the requests sort option. Defaults to relevance.
        :return:
        """
        if hasattr(self, "json") and isinstance(self.json, dict):
            sort_by_str = self.json.get("sort_by", "relevance")
            if sort_by_str in SortFields:
                return SortFields[sort_by_str]
        return SortFields.relevance

    def get_app(self) -> SanicElasticsearch:
        """
        Returns the current SanicElasticsearch app (server)
        :return:
        """
        if isinstance(self.app, SanicElasticsearch):
            return self.app
        raise ValueError("Detected incorrect app initialisation. Expected instance of SanicElasticsearch, got {0}"
                         .format(type(self.app)))
