"""
Mock Elasticsearch client for unit
"""
from elasticsearch import Elasticsearch


class MockElasticsearchClient(Elasticsearch):

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
