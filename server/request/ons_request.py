from sanic.request import Request
from sanic.exceptions import InvalidUsage

from ons.search.sort_fields import SortField
from ons.search.paginator import RESULTS_PER_PAGE

from uuid import uuid4


class ONSRequest(Request):
    """
    Custom ONS request class which implements some useful methods for request parsing
    """

    request_id_log_key = "request_id"
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
