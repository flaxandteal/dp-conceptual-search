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
    except Exception:
        return default


def hash_value(value: str, salt: str = get_salt(), substr_index: int = get_substr_index()) -> str:
    s = "%s%s%s" % (value[substr_index:], salt, value[:substr_index])
    return str(hashlib.sha512(s.encode(sys.getdefaultencoding())).hexdigest())
