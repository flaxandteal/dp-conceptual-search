import os
import logging

from config.utils import read_git_sha

from dp.config.section import Section
from dp.config.utils import bool_env

# APP

APP_CONFIG = Section("APP config")
APP_CONFIG.app_version = read_git_sha()
APP_CONFIG.title = 'dp-conceptual-search'
APP_CONFIG.description = 'Dedicated search API for digital publishing.'


# API

API_CONFIG = Section("API config")
API_CONFIG.enabled_prometheus_metrics = bool_env('ENABLE_PROMETHEUS_METRICS', False)
API_CONFIG.testing = bool_env("TESTING", False)


# ML

ML_CONFIG = Section("Machine Learning config")
ML_CONFIG.supervised_model_filename = os.environ.get("SUPERVISED_MODEL_FILENAME",
                                                     "./unit/ml/test_data/supervised_models/ons_supervised.bin")
ML_CONFIG.unsupervised_model_filename = os.environ.get("UNSUPERVISED_MODEL_FILENAME",
                                                       "./ml/data/word2vec/ons_supervised.vec")


# Elasticsearch

ELASTIC_SEARCH_CONFIG = Section("Elasticsearch config")
ELASTIC_SEARCH_CONFIG.server = os.environ.get("ELASTIC_SEARCH_SERVER", "http://localhost:9200")
ELASTIC_SEARCH_CONFIG.async_enabled = bool_env("ELASTIC_SEARCH_ASYNC_ENABLED", True)
ELASTIC_SEARCH_CONFIG.timeout = int(os.environ.get("ELASTIC_SEARCH_TIMEOUT", 1000))


# Search

SEARCH_CONFIG = Section("Search API config")
SEARCH_CONFIG.default_search_index = "ons"
SEARCH_CONFIG.search_index = os.environ.get("SEARCH_INDEX", SEARCH_CONFIG.default_search_index)
SEARCH_CONFIG.departments_search_index = "departments"
SEARCH_CONFIG.results_per_page = int(os.getenv("RESULTS_PER_PAGE", 10))
SEARCH_CONFIG.max_visible_paginator_link = int(os.getenv("MAX_VISIBLE_PAGINATOR_LINK", 5))
SEARCH_CONFIG.conceptual_search_enabled = bool_env("CONCEPTUAL_SEARCH_ENABLED", False)


# Logging

LOGGING_CONFIG = Section("Logging config")
LOGGING_CONFIG.default_level = logging.INFO
LOGGING_CONFIG.coloured_logging = bool_env('COLOURED_LOGGING_ENABLED', False)
LOGGING_CONFIG.pretty_logging = bool_env('PRETTY_LOGGING', False)
LOGGING_CONFIG.json_logger_indent = 4 if LOGGING_CONFIG.pretty_logging else None
