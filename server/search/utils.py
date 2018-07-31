from sanic.request import Request
from sanic.exceptions import InvalidUsage

from server.requests import get_json_param

from ons.search.indicies import Index
from ons.search.response import ONSResponse
from ons.search.search_engine import AbstractSearchClient

from typing import ClassVar

from inspect import isawaitable


def get_type_filters(request: Request, list_type: str):
    """

    :param request:
    :param list_type:
    :return:
    """
    from ons.search.type_filter import filters_for_type, available_filters

    type_filters_key = get_json_param(
        request, "filter", False, list_type)

    if isinstance(type_filters_key, list):
        return type_filters_key

    available_filters_list = available_filters()
    if type_filters_key is not None and type_filters_key in available_filters_list:
        type_filters = filters_for_type(type_filters_key)
        return type_filters
    else:
        raise InvalidUsage("No such filter type: '%s'" % type_filters_key)


async def content_query(request: Request, search_engine_cls: ClassVar[AbstractSearchClient], list_type: str, **kwargs) -> dict:
    """
    ONS content query
    :param request:
    :param search_engine_cls:
    :param list_type:
    :return:
    """
    from ons.search.sort_fields import SortFields

    search_term = request.args.get("q")
    if search_term is not None:
        app = request.app
        es_client = app.es_client

        # Get any content type filters
        type_filters = get_type_filters(request, list_type)

        # Get sort_by. Default to relevance
        sort_by_str = get_json_param(request, "sort_by", False, "relevance")
        sort_by = SortFields[sort_by_str]

        # Get page_number/size params
        page_number = int(request.args.get("page", 1))
        page_size = int(request.args.get("size", 10))

        params = {**{'type_filters': type_filters, 'sort_by': sort_by}, **kwargs}

        s: AbstractSearchClient = search_engine_cls(
            using=es_client,
            index=Index.ONS.value).content_query(
            search_term,
            page_number,
            page_size,
            **params)

        import os
        from json import dumps
        data = dumps(s.to_dict(), indent=4)
        os.system("echo '%s' | pbcopy" % data)

        response: ONSResponse = s.execute()
        if isawaitable(response):
            response = await response

        result = response.response_to_json(page_number, page_size, sort_by)

        return result
    raise InvalidUsage("no query provided")


async def type_counts_query(request: Request, search_engine_cls: ClassVar[AbstractSearchClient], **kwargs) -> dict:
    """
    ONS type counts query
    :param request:
    :param search_engine_cls:
    :param list_type:
    :return:
    """
    from ons.search.type_filter import default_filters

    search_term = request.args.get("q")
    if search_term is not None:
        app = request.app
        es_client = app.es_client

        s = search_engine_cls(
            using=es_client,
            index=Index.ONS.value).type_counts_query(
            search_term,
            type_filters=default_filters(),
            **kwargs)

        response: ONSResponse = s.execute()
        if isawaitable(response):
            response = await response

        result = response.aggs_to_json()

        return result
    raise InvalidUsage("no query provided")


async def featured_result_query(request: Request, search_engine_cls: ClassVar[AbstractSearchClient], **kwargs) -> dict:
    """
    ONS featured result query
    :param request:
    :param search_engine_cls:
    :return:
    """
    search_term = request.args.get("q")
    if search_term is not None:
        app = request.app
        es_client = app.es_client

        s = search_engine_cls(
            using=es_client,
            index=Index.ONS.value).featured_result_query(
            search_term,
            **kwargs)

        response: ONSResponse = s.execute()
        if isawaitable(response):
            response = await response

        result = response.featured_result_to_json()

        return result
    raise InvalidUsage("no query provided")
