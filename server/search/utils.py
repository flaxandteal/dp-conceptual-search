from sanic.request import Request

from server.search.list_type import ListType


def get_type_filters(request: Request, list_type: ListType):
    """

    :param request:
    :param list_type:
    :return:
    """
    from sanic.exceptions import InvalidUsage

    from server.requests import get_json_param

    from ons.search.type_filter import filters_for_type, available_filters

    type_filters_key = get_json_param(
        request, "filter", False, list_type.value)

    if isinstance(type_filters_key, list):
        return type_filters_key

    available_filters_list = available_filters()
    if type_filters_key is not None and type_filters_key in available_filters_list:
        type_filters = filters_for_type(type_filters_key)
        return type_filters
    else:
        raise InvalidUsage("No such filter type: '%s'" % type_filters_key)
