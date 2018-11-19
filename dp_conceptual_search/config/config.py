import os
import logging

from dp4py_config.section import Section
from dp4py_config.utils import bool_env

from dp4py_sanic.config import CONFIG as SANIC_CONFIG

from dp_conceptual_search.config.utils import read_git_sha


def get_log_level(variable: str, default: str="INFO"):
    """
    Returns the configured log level, and logs error if invalid
    :param variable:
    :param default:
    :return:
    """
    from dp4py_sanic.logging.log_config import get_level_name
    level = os.environ.get(variable, default)
    if isinstance(level, str):
        level = level.upper()

    try:
        return get_level_name(level)
    except NotImplementedError as e:
        logging.error("Caught exception parsing log level", exc_info=e)
        raise SystemExit()


# APP

APP_CONFIG = Section("APP config")
APP_CONFIG.sanic = SANIC_CONFIG
APP_CONFIG.app_version = read_git_sha()
APP_CONFIG.title = 'dp-conceptual-search'
APP_CONFIG.description = 'Dedicated search API for digital publishing.'

# API

API_CONFIG = Section("API config")
API_CONFIG.enabled_prometheus_metrics = bool_env('ENABLE_PROMETHEUS_METRICS', False)
API_CONFIG.testing = bool_env("TESTING", False)
API_CONFIG.conceptual_search_enabled = bool_env("CONCEPTUAL_SEARCH_ENABLED", False)
API_CONFIG.redirect_conceptual_search = bool_env("REDIRECT_CONCEPTUAL_SEARCH", False)

# ML

ML_CONFIG = Section("Machine Learning config")
ML_CONFIG.unsupervised_model_filename = os.environ.get("UNSUPERVISED_MODEL_FILENAME",
                                                       "./dp_conceptual_search/ml/data/word2vec/ons_supervised.vec")

FASTTEXT_CONFIG = Section("FastText config")
FASTTEXT_CONFIG.fastText_host = os.environ.get("DP_FASTTEXT_HOST", "localhost")
FASTTEXT_CONFIG.fastText_port = int(os.environ.get("DP_FASTTEXT_PORT", 5100))
FASTTEXT_CONFIG.num_labels = int(os.environ.get("FASTTEXT_NUM_LABELS", 10))
FASTTEXT_CONFIG.threshold = float(os.environ.get("FASTTEXT_THRESHOLD", 0.0))


# Elasticsearch

ELASTIC_SEARCH_CONFIG = Section("Elasticsearch config")
ELASTIC_SEARCH_CONFIG.server = os.environ.get("ELASTIC_SEARCH_SERVER", "http://localhost:9200")
ELASTIC_SEARCH_CONFIG.async_enabled = bool_env("ELASTIC_SEARCH_ASYNC_ENABLED", True)
ELASTIC_SEARCH_CONFIG.timeout = int(os.environ.get("ELASTIC_SEARCH_TIMEOUT", 1000))
ELASTIC_SEARCH_CONFIG.elasticsearch_log_level = get_log_level("ELASTICSEARCH_LOG_LEVEL", default="INFO")

# Search

SEARCH_CONFIG = Section("Search API config")
SEARCH_CONFIG.default_search_index = "ons"
SEARCH_CONFIG.search_index = os.environ.get("SEARCH_INDEX", SEARCH_CONFIG.default_search_index)
SEARCH_CONFIG.departments_search_index = "departments"
SEARCH_CONFIG.results_per_page = int(os.getenv("RESULTS_PER_PAGE", 10))
SEARCH_CONFIG.max_visible_paginator_link = int(os.getenv("MAX_VISIBLE_PAGINATOR_LINK", 5))
SEARCH_CONFIG.max_request_size = int(os.getenv("SEARCH_MAX_REQUEST_SIZE", 200))
