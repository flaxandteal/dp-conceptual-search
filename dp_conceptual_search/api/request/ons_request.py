from typing import List
from ujson import loads

from sanic.exceptions import InvalidUsage

from dp4py_sanic.api.request import Request

from dp_conceptual_search.config import SEARCH_CONFIG

from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.type_filter import TypeFilter, AvailableTypeFilters
from dp_conceptual_search.ons.search.exceptions.unknown_type_filter_exception import UnknownTypeFilter

from dp_conceptual_search.api.log import logger
from dp_conceptual_search.api.search.list_type import ListType


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
        Returns the requested page size (min of 1). Defaults to the value set by the paginator.
        :return:
        """
        page_size = self.args.get("size", SEARCH_CONFIG.results_per_page)
        if isinstance(page_size, str):
            if page_size.isdigit():
                page_size = int(page_size)
            else:
                # Log error parsing param to int
                message = "Unable to convert size param to int"
                logger.error(self.request_id, message, extra={"size": page_size})
                raise InvalidUsage(message)

        if isinstance(page_size, int) and page_size > 0:
            return page_size

        # Raise InvalidUsage (400) and log error
        message = "Invalid request [size={size}]".format(size=page_size)
        logger.error(self.request_id, message, extra={"size": page_size})
        raise InvalidUsage(message)

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
