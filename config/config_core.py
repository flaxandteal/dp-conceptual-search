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


API_VERSION = '1.0.1'
API_TITLE = 'dp-conceptual-search'
API_DESCRIPTION = 'Dedicated search API for digital publishing.'

# General

LOGO = None  # Disable printing of the Sanic logo
RESPONSE_TIMEOUT = 600
SEARCH_CONFIG = os.environ.get('SEARCH_CONFIG', 'development')

# Elasticsearch

ELASTIC_SEARCH_SERVER = os.environ.get("ELASTIC_SEARCH_SERVER", "http://localhost:9200")
ELASTIC_SEARCH_ASYNC_ENABLED = bool_env("ELASTIC_SEARCH_ASYNC_ENABLED", True)
ELASTIC_SEARCH_TIMEOUT = int(os.environ.get("ELASTIC_SEARCH_TIMEOUT", 1000))

# mongoDB

MONGO_SEARCH_DATABASE = os.environ.get('MONGO_SEARCH_DATABASE', 'local')
MONGO_DEFAULT_HOST = os.environ.get("MONGO_DEFAULT_HOST", "localhost")
MONGO_DEFAULT_PORT = os.environ.get("MONGO_DEFAULT_PORT", 27017)
MONGO_BIND_ADDR = 'mongodb://{host}:{port}'.format(
    host=MONGO_DEFAULT_HOST, port=MONGO_DEFAULT_PORT)

# Motor client

MOTOR_URI = "{bind_addr}/{db}".format(
    bind_addr=MONGO_BIND_ADDR,
    db=MONGO_SEARCH_DATABASE
)

# ML

ML_DATA_DIR = os.environ.get("ML_DATA_DIR", "./ml/data/")
SUPERVISED_MODELS_DIR = os.environ.get("SUPERVISED_MODELS_DIR", "supervised_models/")
UNSUPERVISED_MODELS_DIR = os.environ.get("UNSUPERVISED_MODELS_DIR", "word2vec/")
SUPERVISED_MODEL_NAME = os.environ.get("SUPERVISED_MODEL_NAME", "ons_supervised.bin")
UNSUPERVISED_MODEL_NAME = os.environ.get("UNSUPERVISED_MODEL_NAME", "ons_supervised.vec")

# Search

RESULTS_PER_PAGE = int(os.getenv("RESULTS_PER_PAGE", 10))
MAX_VISIBLE_PAGINATOR_LINK = int(os.getenv("MAX_VISIBLE_PAGINATOR_LINK", 5))

# Conceptual search

CONCEPTUAL_SEARCH_ENABLED = bool_env('CONCEPTUAL_SEARCH_ENABLED', False)

# User recommendation

USER_RECOMMENDATION_ENABLED = bool_env('USER_RECOMMENDATION_ENABLED', False)

if USER_RECOMMENDATION_ENABLED and not CONCEPTUAL_SEARCH_ENABLED:
    # Can't have user recommendation without conceptual search
    raise SystemExit("ERROR: User recommendation requires conceptual search")

# Prometheus metrics endpoint

ENABLE_PROMETHEUS_METRICS = bool_env('ENABLE_PROMETHEUS_METRICS', False)

# Logging

COLOURED_LOGGING_ENABLED = bool_env('COLOURED_LOGGING_ENABLED', False)
PRETTY_LOGGING = bool_env('PRETTY_LOGGING', False)
JSON_LOGGER_INDENT = 4 if PRETTY_LOGGING else None
