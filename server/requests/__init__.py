from sanic.exceptions import InvalidUsage

def _get_param(request, key, required, args, generator, default):
    if key in args:
        values = generator(key)
        if values is not None and len(values) > 0:
            if len(values) == 1:
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


def get_request_param(request, key, required, default=None):
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


def get_form_param(request, key, required, default=None):
    """

    :param request: Sanic request
    :param key:
    :param required:
    :param default:
    :return:
    """
    value = _get_param(
        request,
        key,
        required,
        request.form,
        request.form.getlist,
        default)
    return value
