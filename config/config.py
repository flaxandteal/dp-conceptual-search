import os
from config.section import Section
from config.utils import bool_env


# API

API_CONFIG = Section("APi specific config")
API_CONFIG.version = '1.0.1'
API_CONFIG.title = 'dp-conceptual-search'
API_CONFIG.description = 'Dedicated search API for digital publishing.'
API_CONFIG.enabled_prometheus_metrics = bool_env('ENABLE_PROMETHEUS_METRICS', False)
API_CONFIG.search_config = os.environ.get("SEARCH_CONFIG", "sanic")


# Elasticsearch

ELASTIC_SEARCH_CONFIG = Section("Elasticsearch specific config")
ELASTIC_SEARCH_CONFIG.server = os.environ.get("ELASTIC_SEARCH_SERVER", "http://localhost:9200")
ELASTIC_SEARCH_CONFIG.async_enabled = bool_env("ELASTIC_SEARCH_ASYNC_ENABLED", True)
ELASTIC_SEARCH_CONFIG.timeout = int(os.environ.get("ELASTIC_SEARCH_TIMEOUT", 1000))

# mongoDB

MONGO_CONFIG = Section("mongoDB specific config")
MONGO_CONFIG.db = os.environ.get('MONGO_SEARCH_DATABASE', 'local')
MONGO_CONFIG.host = os.environ.get("MONGO_DEFAULT_HOST", "localhost")
MONGO_CONFIG.port = os.environ.get("MONGO_DEFAULT_PORT", 27017)
MONGO_CONFIG.bind_addr = 'mongodb://{host}:{port}'.format(
    host=MONGO_CONFIG.host, port=MONGO_CONFIG.port)

# Search

SEARCH_CONFIG = Section("Search specific config")
SEARCH_CONFIG.results_per_page = int(os.getenv("RESULTS_PER_PAGE", 10))
SEARCH_CONFIG.max_visible_paginator_link = int(os.getenv("MAX_VISIBLE_PAGINATOR_LINK", 5))

# Logging

LOGGING_CONFIG = Section("Logging specific config")
LOGGING_CONFIG.coloured_logging = bool_env('COLOURED_LOGGING_ENABLED', False)
LOGGING_CONFIG.pretty_logging = bool_env('PRETTY_LOGGING', False)
LOGGING_CONFIG.json_logger_indent = 4 if LOGGING_CONFIG.pretty_logging else None
