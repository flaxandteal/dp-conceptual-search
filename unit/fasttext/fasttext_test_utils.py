"""
Provides method to mock in for get_fasttext_client
"""
from dp_fasttext.client.testing.mock_client import MockClient


class MockHealthyClient(MockClient):
    async def _get(self, uri: str, **kwargs):
        if uri == self._health_uri:
            return {}, kwargs.get("headers", {})
        else:
            raise NotImplementedError("GET request for uri '{0}' not implemented".format(uri))


class MockUnHealthyClient(MockClient):
    async def _get(self, uri: str, **kwargs):
        if uri == self._health_uri:
            raise Exception("Mock exception")
        else:
            raise NotImplementedError("GET request for uri '{0}' not implemented".format(uri))


def mock_fasttext_client():
    """
    Returns a mock fasttext HTTP client
    :return:
    """
    return MockHealthyClient()


def mock_unhealthy_fasttext_client():
    """
    Returns a mock fasttext HTTP client
    :return:
    """
    return MockUnHealthyClient()
