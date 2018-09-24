"""
Initialises APP wide logging config
"""
from dp.log.config import config_for_formatter

from api.log.formatter import SearchJsonFormatter

supported_keys = [
    'timestamp',
    'level',
    'pathname',
    'funcName',
    'lineno',
    'module',
    'message',
    'name',
    'pathname'
]

log_config = config_for_formatter(SearchJsonFormatter, supported_keys)
