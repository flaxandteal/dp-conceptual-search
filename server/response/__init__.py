import six
from sanic.response import json as sanic_json

from .encoders import AutoJSONEncoder


def is_iterable(x):
    try:
        iter(x)
        return True
    except TypeError:
        return False


def serializer_func_mapper(x, fn):
    if isinstance(x, six.text_type):
        return six.text_type(x)
    if isinstance(x, six.integer_types):
        return int(x)
    if isinstance(x, dict):
        return {k: serializer_func_mapper(v, fn) for k, v in x.items()}
    if is_iterable(x):
        return [serializer_func_mapper(item, fn) for item in x]
    return fn(x)


def json(data, **kwargs):
    if data is None:
        return bytes()
    encoder = AutoJSONEncoder().default
    return sanic_json(serializer_func_mapper(data, encoder))
