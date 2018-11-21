from typing import List, Optional

from sanic.exceptions import InvalidUsage

from dp4py_sanic.api.request import Request

from dp_conceptual_search.log import logger
from dp_conceptual_search.config import SEARCH_CONFIG, FASTTEXT_CONFIG

from dp_conceptual_search.ons.search.sort_fields import SortField
from dp_conceptual_search.ons.search.content_type import AvailableContentTypes, ContentType


class ONSRequest(Request):
    """
    Custom ONS request class which implements some useful methods for request parsing
    """
    def get_search_term(self) -> Optional[str]:
        """
        Parses the request to extract a search term
        :return:
        """
        search_term = self.args.get("q", None)
        if search_term is None:
            logger.error(self.request_id, "Search term not specified", extra={
                "status": 400
            })
            raise InvalidUsage("Search term not specified")
        return search_term

    def get_uri(self) -> Optional[str]:
        """
        Returns the uri param from the POST data
        :return:
        """
        if hasattr(self, "json") and isinstance(self.json, dict):
            if "uri" not in self.json:
                logger.error(self.request_id, "uri parameter not found in POST data", extra={
                    "status": 4000
                })
                raise InvalidUsage("uri parameter not found in POST data")
            return self.json.get("uri")
        message = "Invalid request body whilst trying to parse body for uri"
        logger.error(self.request_id, message, extra={
            "status": 400
        })
        raise InvalidUsage(message)

    def get_current_page(self) -> int:
        """
        Returns the requested page number. Defaults to the first page.
        :return:
        """
        current_page = self.args.get("page", 1)
        return int(current_page)

    def get_page_size(self) -> Optional[int]:
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

    def get_type_filters(self) -> Optional[List[ContentType]]:
        """
        Returns requested type filters
        :return:
        """
        if hasattr(self, "json") and isinstance(self.json, dict):
            json: dict = self.json
            if "filter" in json and isinstance(json.get("filter"), list):
                filters: List[str] = self.json.get("filter")

                content_type_filters: List[ContentType] = []
                for content_filter in filters:
                    if AvailableContentTypes.is_content_type(content_filter):
                        content_type_filters.append(AvailableContentTypes.from_str(content_filter))
                    else:
                        logger.error(self.request_id, "Unknown content type for filter", extra={
                            "params": {
                                "type": content_filter
                            }
                        })
                        raise InvalidUsage("Unknown content type for filter [%s]" % content_filter)

                return content_type_filters

        # Return all known content types
        return AvailableContentTypes.available_content_types()

    def get_num_labels(self) -> int:
        """
        Returns the requested number of labels. Defaults to config value.
        :return:
        """
        current_page = self.args.get("num_labels", FASTTEXT_CONFIG.num_labels)
        return int(current_page)

    def get_elasticsearch_query(self) -> Optional[dict]:
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
