from sanic.request import Request
from sanic.exceptions import InvalidUsage


def _get_param(request: Request, key, required, args, generator, default):
    if key in args:
        values = generator(key)
        if values is not None:
            if hasattr(values, "__iter__") and len(values) == 1:
                return values[0]
            else:
                return values

    if required:
        message = "Invalid value for required argument '%s' and route '%s'" % (
            key, request.url)
        # Will be automatically caught by handle_exception and return a 400
        raise InvalidUsage(message)
    else:
        return default


def get_request_param(request: Request, key, required, default=None):
    """
    Simple util function for extracting parameters from requests.
    :param request: Sanic request
    :param key:
    :param required:
    :param default:
    :return: value
    :raises ValueError: key not found or value is None
    """
    return _get_param(
        request,
        key,
        required,
        request.args,
        request.args.getlist,
        default)


def get_form_param(request: Request, key, required, default=None):
    """

    :param request: Sanic request
    :param key:
    :param required:
    :param default:
    :return:
    """
    return _get_param(
        request,
        key,
        required,
        request.form,
        request.form.getlist,
        default)


def get_json_param(request: Request, key, required, default=None):
    from json import loads, JSONDecodeError
    from sanic.exceptions import InvalidUsage

    try:
        val = _get_param(
            request,
            key,
            required,
            request.json,
            request.json.get,
            default)

        try:
            return loads(val)
        except JSONDecodeError:
            return val
    except (AttributeError, InvalidUsage):
        return get_form_param(request, key, required, default=default)


def extract_page(request: Request) -> int:
    """
    Extract page number from request
    """
    return int(request.args.get("page", 1))


def extract_page_size(request: Request) -> int:
    """
    Extract page size from request
    Maximum page size is set to 10000
    """
    return min(int(request.args.get("size", 10)), 10000)
