"""
Mock Elasticsearch client for unit
"""
from elasticsearch import Elasticsearch
from elasticsearch.client import ClusterClient


class MockClusterClient(ClusterClient):
    """
    Mocks out functionality from the Elasticsearch ClusterClient
    """
    def health(self, index=None, params=None):
        raise NotImplementedError("health not implemented, must be mocked!")


class MockElasticsearchClient(Elasticsearch):
    """
    Mocks out functionality from the Elasticsearch client
    """
    def __init__(self, *args, **kwargs):
        """
        Sets cluster client to be MockClusterClient
        """
        super(MockElasticsearchClient, self).__init__(*args, **kwargs)

        self.cluster = MockClusterClient(self)

    def index(self, index, doc_type, body, id=None, params=None):
        raise NotImplementedError("Index not implemented")

    def delete(self, index, doc_type, id, params=None):
        raise NotImplementedError("Delete not implemented")

    def search(self, index=None, doc_type=None, body=None, params=None):
        """
        Mocks the search API
        :param index:
        :param doc_type:
        :param body:
        :param params:
        :return:
        """
        raise NotImplementedError("search not implemented, must be mocked!")
