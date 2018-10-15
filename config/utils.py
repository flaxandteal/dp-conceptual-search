import os
import git
import logging
from typing import Optional


def git_sha() -> Optional[str]:
    """
    Returns the sha of the latest git commit
    :return:
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha

        return sha
    except Exception as e:
        logging.error("Unable to get git commit sha", exc_info=e)
    return None


def bool_env(var_name, default=False):
    """
    Get an environment variable coerced to a boolean value.
    Example:
        Bash:
            $ export SOME_VAL=True
        settings.py:
            SOME_VAL = bool_env('SOME_VAL', False)
    Arguments:
        var_name: The name of the environment variable.
        default: The default to use if `var_name` is not specified in the
                 environment.
    Returns: `var_name` or `default` coerced to a boolean using the following
        rules:
            "False", "false", "" or 0 => False
            Any other non-empty string => True
    """
    test_val = os.environ.get(var_name, default)
    # Explicitly check for 'False', 'false', and '0' since all non-empty
    # string are normally coerced to True.
    if test_val in ('False', 'false', '0'):
        return False
    return bool(test_val)
