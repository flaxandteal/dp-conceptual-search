import abc
import unittest
from unittest.mock import MagicMock

from unit.utils.elasticsearch_test_utils import ElasticsearchTestUtils


class ElasticsearchTestCase(unittest.TestCase, ElasticsearchTestUtils, abc.ABC):
    """
    A test class for working with Elasticsearch
    """

    def setUp(self):
        from unit.mocks.mock_es_client import MockElasticsearchClient

        hits = self.mock_hits()

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

        # Mock the search client
        self.mock_client = MockElasticsearchClient()
        self.mock_client.search = MagicMock(return_value=response)
