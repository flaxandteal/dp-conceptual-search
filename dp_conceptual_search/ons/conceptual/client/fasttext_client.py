"""
Provides methods for initialising dp-fasttext HTTP client
"""
from dp_fasttext.client import Client

from dp_conceptual_search.config.config import FASTTEXT_CONFIG


class FastTextClientService(object):
    @staticmethod
    def get_fasttext_client() -> Client:
        return Client(FASTTEXT_CONFIG.fasttext_host, FASTTEXT_CONFIG.fasttext_port)
