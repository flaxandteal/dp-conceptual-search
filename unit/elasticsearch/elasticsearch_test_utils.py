from numpy.random import rand

from unittest.mock import MagicMock
from unit.mocks.mock_es_client import MockElasticsearchClient

from dp_fasttext.ml.utils import encode_float_list

from dp_conceptual_search.ons.search.fields import Field, AvailableFields


def mock_search_client(*args):
    """
    Returns a mock Elasticsearch client for search
    :return:
    """
    # Mock the search client
    mock_client = MockElasticsearchClient()
    mock_client.search = MagicMock(return_value=mock_search_response())

    return mock_client


def mock_shards_json() -> dict:
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


def mock_single_hit() -> list:
    """
    Mocks a single hit with an encoded embedding vector
    :return:
    """
    embedding_vector_field: Field = AvailableFields.EMBEDDING_VECTOR.value

    test_vector = rand(10)
    test_vector_encoded = encode_float_list(list(test_vector.tolist()))
    hit = {
        "_id": "test 1",
        "_type": "ghostbuster",
        "_source": {
            "name": "Egon Spengler",
            "occupation": "Ghostbuster",
            "location": "New York City, New York",
            "description": {
                "keywords": ["Test"]
            },
            embedding_vector_field.name: test_vector_encoded
        },
    }

    return [hit]


def mock_hits() -> list:
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
                "location": "New York City, New York",
                "description": {
                    "keywords": ["Test"]
                }
            },
        },
        {
            "_id": "test 2",
            "_type": "ghostbuster",
            "_source": {
                "name": "Peter Venkman",
                "occupation": "Ghostbuster",
                "location": "New York City, New York",
                "description.keywords": {
                    "keywords": ["Test"]
                }
            }
        },
        {
            "_id": "test 3",
            "_type": "not_a_ghostbuster",
            "_source": {
                "name": "Zuul",
                "occupation": "Not a Ghostbuster",
                "location": "New York City, New York",
                "description": {
                    "keywords": ["Zuul", "Test"]
                }
            },
            "highlight": {
                "description.keywords": [
                    "<strong>Zuul</strong>"
                ]
            }
        }
    ]
    return hits


def mock_hits_highlighted() -> list:
    """
    Returns the list of mock hits to be used for tests
    :return:
    """
    hits = [
        {
            "name": "Egon Spengler",
            "occupation": "Ghostbuster",
            "location": "New York City, New York",
            "_type": "ghostbuster",
            "description": {
                "keywords": ["Test"]
            }
        },
        {
            "name": "Peter Venkman",
            "occupation": "Ghostbuster",
            "location": "New York City, New York",
            "_type": "ghostbuster",
            "description.keywords": {
                "keywords": ["Test"]
            }
        },
        {
            "name": "Zuul",
            "occupation": "Not a Ghostbuster",
            "location": "New York City, New York",
            "_type": "not_a_ghostbuster",
            "description": {
                "keywords": ["<strong>Zuul</strong>", "Test"]
            }
        }
    ]
    return hits


def mock_search_response(hits=None):
    """
    Returns a full mock response to be used for testing
    :return:
    """
    if hits is None:
        hits = mock_hits()

    response = {
        "_shards": mock_shards_json(),
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
        "timed_out": False,
        "took": 5
    }

    return response


def mock_health_response(status):
    """
    Mocks the cluster health response
    :return:
    """
    response = {
        "cluster_name": "elasticsearch",
        "status": status,
        "timed_out": False,
        "number_of_nodes": 1,
        "number_of_data_nodes": 1,
        "active_primary_shards": 9,
        "active_shards": 9,
        "relocating_shards": 0,
        "initializing_shards": 0,
        "unassigned_shards": 5,
        "delayed_unassigned_shards": 0,
        "number_of_pending_tasks": 0,
        "number_of_in_flight_fetch": 0,
        "task_max_waiting_in_queue_millis": 0,
        "active_shards_percent_as_number": 64.2857142857
    }

    return response
