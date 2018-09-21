"""
Initialises APP wide logging config
"""
from dp.log.config import config_for_formatter
from dp.log.formatters import PrettyCustomJsonFormatter

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

log_config = config_for_formatter(PrettyCustomJsonFormatter, supported_keys)
