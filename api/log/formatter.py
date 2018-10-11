"""
Add namespace to all log messages
"""
from config import API_CONFIG, LOGGING_CONFIG
from dp.log.formatters import CustomJsonFormatter


class SearchJsonFormatter(CustomJsonFormatter):
    def __init__(self, *args, **kwargs):
        super(SearchJsonFormatter, self).__init__(
            *args, json_indent=LOGGING_CONFIG.json_logger_indent, coloured_logging=LOGGING_CONFIG.coloured_logging, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(SearchJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['namespace'] = API_CONFIG.title
