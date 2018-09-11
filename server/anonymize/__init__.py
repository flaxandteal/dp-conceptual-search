import os
import sys
import hashlib


def get_salt() -> str:
    return os.environ.get("GA_SALT", "")


def get_substr_index(default: int=0) -> int:
    try:
        substr_idx = int(os.environ.get("GA_SUBSTR_INDEX", default))

        if not isinstance(substr_idx, int):
            return default
        return substr_idx
    except ValueError as e:
        from sanic.log import logger
        logger.error("Error getting GA_SUBSTR_INDEX env var", e)
        return default


_default_salt = get_salt()
_default_substr_index = get_substr_index()


def hash_value(value: str, salt: str = _default_salt, substr_index: int = _default_substr_index) -> str:
    s = "%s%s%s" % (value[substr_index:], salt, value[:substr_index])
    return str(hashlib.sha512(s.encode(sys.getdefaultencoding())).hexdigest())
