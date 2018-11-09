"""
Provides method to mock in for get_fasttext_client
"""
from dp_fasttext.client.testing.mock_client import MockClient


def mock_fasttext_client():
    """
    Returns a mock fasttext HTTP client
    :return:
    """
    return MockClient()
