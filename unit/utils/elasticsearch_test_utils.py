"""
Helper class for testing with Elasticsearch
"""


class ElasticsearchTestUtils(object):
    """
    A test class for working with Elasticsearch
    """
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

    @staticmethod
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
