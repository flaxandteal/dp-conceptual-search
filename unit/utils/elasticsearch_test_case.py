import abc
import unittest
from unittest.mock import MagicMock

from unit.mocks.mock_es_client import MockElasticsearchClient


class ElasticsearchTestCase(unittest.TestCase, abc.ABC):
    """
    A test class for working with Elasticsearch
    """

    def setUp(self):
        response = self.mock_response

        # Mock the search client
        self.mock_client = MockElasticsearchClient()
        self.mock_client.search = MagicMock(return_value=response)

    @property
    def mock_shards_json(self) -> dict:
        """
        Returns mock shards JSON for testing
        :return:
        """
        shards = {
            "failed": 0,
            "successful": 9,
            "total": 9
        }

        return shards

    @property
    def mock_timed_out(self) -> bool:
        """
        Returns mock value for timed_out to be used for testing
        :return:
        """
        return False

    @property
    def mock_took(self) -> int:
        """
        Returns the mock took value to be used for testing
        :return:
        """
        return 5

    @property
    def mock_hits(self) -> list:
        """
        Returns the list of mock hits to be used for tests
        :return:
        """
        hits = [
            {
                "_id": "test 1",
                "_type": "ghostbuster",
                "_source": {
                    "name": "Egon Spengler",
                    "occupation": "Ghostbuster",
                    "location": "New York City, New York"
                }
            },
            {
                "_id": "test 2",
                "_type": "ghostbuster",
                "_source": {
                    "name": "Peter Venkman",
                    "occupation": "Ghostbuster",
                    "location": "New York City, New York"
                }
            },
            {
                "_id": "test 3",
                "_type": "not_a_ghostbuster",
                "_source": {
                    "name": "Zuul",
                    "occupation": "Not a Ghostbuster",
                    "location": "New York City, New York"
                }
            }
        ]
        return hits

    @property
    def mock_response(self):
        """
        Returns a full mock response to be used for testing
        :return:
        """
        hits = self.mock_hits
        response = {
            "_shards": self.mock_shards_json,
            "hits": {
                "hits": hits,
                "max_score": 1.0,
                "total": len(hits)
            },
            "aggregations": {
                "docCounts": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [
                        {
                            "key": "ghostbuster",
                            "doc_count": 2
                        },
                        {
                            "key": "not_a_ghostbuster",
                            "doc_count": 1
                        }
                    ]
                }
            },
            "timed_out": self.mock_timed_out,
            "took": self.mock_took
        }

        return response
