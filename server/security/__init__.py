import os
import sys
import hashlib


def get_salt():
    return os.environ.get("GA_SALT", "")


def get_substr_index():
    return int(os.environ.get("GA_SUBSTR_INDEX", 0))


def hash_value(value):
    salt = get_salt()
    substr_index = get_substr_index()
    s = "%s%s%s" % (value[substr_index:], value[:substr_index], salt)
    return str(hashlib.sha512(s.encode(sys.getdefaultencoding())).hexdigest())
