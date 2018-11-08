"""
Mock fasttext client for unit testing
"""
from dp_fasttext.client import Client


def mock_labels_api() -> dict:
    """
    Returns mock labels and their probabilities
    :return:
    """
    labels = ['economy', 'inflation']
    probabilities = [0.8, 0.4]

    return {
        "labels": labels,
        "probabilities": probabilities
    }


def mock_sentence_vector(data: dict) -> dict:
    """
    Returns a mock sentence vector
    :return:
    """
    vector = [1.0, 0.5, 0.0]
    return {
        "query": data.get("query"),
        "vector": vector
    }


class MockClient(Client):

    def __init__(self):
        super(MockClient, self).__init__("test", 1234)

    async def _post(self, uri: str, data: dict, **kwargs) -> tuple:
        headers = self.get_headers()
        if uri == self._predict_uri:
            json = mock_labels_api()
        elif uri == self._sentence_vector_uri:
            json = mock_sentence_vector(data)
        else:
            raise NotImplementedError("No mock for uri '{0}'".format(uri))

        return json, headers
