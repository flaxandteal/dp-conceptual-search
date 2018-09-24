"""
Add namespace to all log messages
"""
from config.config_core import API_TITLE, JSON_LOGGER_INDENT
from dp.log.formatters import CustomJsonFormatter


class SearchJsonFormatter(CustomJsonFormatter):
    def __init__(self, *args, **kwargs):
        super(SearchJsonFormatter, self).__init__(
            *args, json_indent=JSON_LOGGER_INDENT, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(SearchJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['namespace'] = API_TITLE
