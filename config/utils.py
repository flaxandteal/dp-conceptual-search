"""
Util methods for app config
"""
import os
from typing import Optional


def read_git_sha() -> Optional[str]:
    """
    Reads the 'app_version' file and returns the git sha
    :return:
    """
    path = os.path.dirname(__file__)
    fname = "{path}/../app_version".format(path=path)
    with open(fname, "r") as f:
        git_sha = f.read()
        if git_sha is not None:
            return git_sha.rstrip()
