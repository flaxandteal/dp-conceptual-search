"""
Provides methods for initialising dp-fastText HTTP client
"""
from dp_fasttext.client import Client

from dp_conceptual_search.config.config import ML_CONFIG


def get_fasttext_client() -> Client:
    return Client(ML_CONFIG.fastText_host, ML_CONFIG.fastText_port)
