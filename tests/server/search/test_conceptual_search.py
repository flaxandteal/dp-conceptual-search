import unittest
from tests.server.test_app import TestApp


class ConceptualSearchTestSuite(TestApp):

    search_term = "rpi"
    uri_prefix = "/search/concptual/ons"

    maxDiff = None

    def search_and_assert(self, list_type: str):
        """
        Tests the ONS search API for a specified list_type
        :param list_type:
        :return:
        """
        from tests.server.search.dummy_documents import test_document

        target = "/search/%s/content?q=%s" % (list_type, self.search_term)

        request, response = self.get(target, 200)

        # Check the search results
        json_data = response.json

        self.assertIsNotNone(json_data, "json response should not be none")
        self.assertIsInstance(
            json_data,
            dict,
            "json response should be instance of dict")

        expected_keys = [
            'numberOfResults',
            'took',
            'results',
            'paginator',
            'sortBy']
        for key in expected_keys:
            self.assertIn(key, json_data)

        # Make sure we got the document we expected
        self.assertEqual(json_data['numberOfResults'], 1)

        doc = json_data['results'][0]
        test_source = test_document['_source']
        self.assertEqual(doc['type'], test_source['type'])
        self.assertEqual(doc['uri'], test_source['uri'])
        self.assertEqual(doc['description'], test_source['description'])

    def count_and_assert(self, list_type: str):
        """
        Tests the ONS aggregations API for a specified list_type
        :param list_type:
        :return:
        """
        from tests.server.search.dummy_documents import test_aggs

        target = "/search/%s/counts?q=%s" % (list_type, self.search_term)

        request, response = self.get(target, 200)

        # Check the search results
        json_data = response.json

        self.assertIsNotNone(json_data, "json response should not be none")
        self.assertIsInstance(
            json_data,
            dict,
            "json response should be instance of dict")

        expected_keys = ['numberOfResults', 'docCounts']
        for key in expected_keys:
            self.assertIn(key, json_data)

        # Make sure we got the aggregations we expected
        total_expected = 409
        self.assertEqual(json_data['numberOfResults'], total_expected)

        doc_counts: dict = json_data['docCounts']
        self.assertIsInstance(doc_counts, dict)

        expected_buckets = test_aggs.get("buckets")

        for bucket in expected_buckets:
            key = bucket.get('key')
            counts = bucket.get('doc_count')

            self.assertIn(key, doc_counts)
            self.assertEqual(doc_counts.get(key), counts)

    def test_search(self):
        """
        Tests the default ONS content search
        :return:
        """
        self.search_and_assert("ons")

    def test_search_data(self):
        """
        Tests the ONS search_data API
        :return:
        """
        self.search_and_assert("onsdata")

    def test_search_publications(self):
        """
        Tests the ONS search_publications API
        :return:
        """
        self.search_and_assert("onspublications")

    def test_counts(self):
        """
        Tests the default ONS content search
        :return:
        """
        self.count_and_assert("ons")

    def test_counts_data(self):
        """
        Tests the ONS search_data API
        :return:
        """
        self.count_and_assert("onsdata")

    def test_counts_publications(self):
        """
        Tests the ONS search_publications API
        :return:
        """
        self.count_and_assert("onspublications")


if __name__ == "__main__":
    unittest.main()
