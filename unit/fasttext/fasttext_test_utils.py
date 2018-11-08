"""
Provides method to mock in for get_fasttext_client
"""
from unit.mocks.mock_fasttext_client import MockClient


def mock_fasttext_client():
    """
    Returns a mock fasttext HTTP client
    :return:
    """
    return MockClient()
