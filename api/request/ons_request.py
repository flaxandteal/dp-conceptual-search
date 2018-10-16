from uuid import uuid4
from typing import List
from ujson import loads

from sanic.request import Request
from sanic.exceptions import InvalidUsage

from ons.search.sort_fields import SortField
from ons.search.paginator import RESULTS_PER_PAGE
from ons.search.type_filter import TypeFilter, AvailableTypeFilters
from ons.search.exceptions.unknown_type_filter_exception import UnknownTypeFilter

from api.log import logger
from api.search.list_type import ListType


class ONSRequest(Request):
    """
    Custom ONS request class which implements some useful methods for request parsing
    """
    request_id_header = "X-Request-Id"

    def __init__(self, *args, **kwargs):
        """
        Initialise the request object with a unique ID (either supplied as a header or generated)
        :param args:
        :param kwargs:
        """
        super(ONSRequest, self).__init__(*args, **kwargs)

        # Init empty request ID
        self.request_id = None

        # Check for existing ID
        if self.request_id_header in self.headers:
            self.request_id = self.headers.get(self.request_id_header)
        else:
            # Generate a random uuid4
            self.request_id = str(uuid4())

    def get_search_term(self) -> str:
        """
        Parses the request to extract a search term
        :return:
        """
        search_term = self.args.get("q", None)
        if search_term is None:
            logger.error(self.request_id, "Search term not specified", extra={"status": 400})
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

    def get_sort_by(self) -> SortField:
        """
        Returns the requests sort option. Defaults to relevance.
        :return:
        """
        if hasattr(self, "json") and isinstance(self.json, dict):
            sort_by_str = self.json.get("sort_by", "relevance")
            if SortField.is_sort_field(sort_by_str):
                return SortField.from_str(sort_by_str)
        return SortField.relevance

    def get_type_filters(self, list_type: ListType) -> List[TypeFilter]:
        """
        Returns requested type filters or the defaults for the desired ListType
        :param list_type:
        :return:
        """
        if hasattr(self, "json") and isinstance(self.json, dict):
            type_filters_raw = self.json.get("filter", None)

            if type_filters_raw is not None:
                if isinstance(type_filters_raw, str):
                    type_filters_raw = loads(type_filters_raw)

                if not isinstance(type_filters_raw, list):
                    type_filters_raw = [type_filters_raw]

                try:
                    type_filters: List[TypeFilter] = AvailableTypeFilters.from_string_list(type_filters_raw)
                    return type_filters
                except UnknownTypeFilter as e:
                    # Import logger here to prevent circular dependency on module import
                    message = "Received unknown type filter: '{0}'".format(e.unknown_type_filter)
                    logger.error(self.request_id, message, exc_info=e)
                    raise InvalidUsage(message)

        return list_type.to_type_filters()

    def get_elasticsearch_query(self) -> dict:
        """
        Parse the request body for Elasticsearch query JSON and return as dict
        :return:
        """
        body = self.json

        if body is not None and isinstance(body, dict) and "query" in body:
            return body
        else:
            # Raise InvalidUsage (400) and log error
            # Import logger here to prevent circular dependency on module import
            message = "Invalid request body whilst trying to parse for Elasticsearch query"
            logger.error(self.request_id, message, extra={"body": body})
            raise InvalidUsage(message)
