import os


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
            "False", "false" or "" => False
            Any other non-empty string => True
    """
    test_val = os.environ.get(var_name, default)
    # Explicitly check for 'False', 'false', and '0' since all non-empty
    # string are normally coerced to True.
    if test_val in ('False', 'false', '0'):
        return False
    return bool(test_val)


LOGO = None

MONGO_SEARCH_DATABASE = os.environ.get('MONGO_SEARCH_DATABASE', 'local')

MONGO_DEFAULT_HOST = os.environ.get("MONGO_DEFAULT_HOST", "localhost")
MONGO_DEFAULT_PORT = os.environ.get("MONGO_DEFAULT_PORT", 27017)

MONGO_BIND_ADDR = 'mongodb://{host}:{port}'.format(
    host=MONGO_DEFAULT_HOST, port=MONGO_DEFAULT_PORT)

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)

# Conceptual search
CONCEPTUAL_SEARCH_ENABLED = bool_env('CONCEPTUAL_SEARCH_ENABLED', False)

# User recommendation
USER_RECOMMENDATION_ENABLED = bool_env('USER_RECOMMENDATION_ENABLED', False)

# Prometheus metrics endpoint
ENABLE_PROMETHEUS_METRICS = bool_env('ENABLE_PROMETHEUS_METRICS', False)

# Logging
COLOURED_LOGGING_ENABLED = bool_env('COLOURED_LOGGING_ENABLED', False)
