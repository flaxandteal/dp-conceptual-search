import unittest
from tests.server.test_app import TestApp


class ConceptualSearchTestSuite(TestApp):

    search_term = "rpi"

    def check_search_result(self, result, expected_document: dict):
        # Assert result contains correct keys
        expected_result_keys = [
            'numberOfResults',
            'took',
            'results',
            'paginator',
            'sortBy']

        for k in expected_result_keys:
            self.assertIn(k, result, "result does not contain key '%s'" % k)

        # Assert the result contains the expected document
        numberOfResults = result['numberOfResults']
        self.assertEqual(numberOfResults, 1, "expected one result")

        hits = result['results']
        self.assertIsNotNone(hits, "hits should not be none")
        self.assertIsInstance(hits, list, "hits should be instance of list")

        hit = hits[0]
        # Make sure the hit was marshalled correctly
        self.assertEqual(hit['_type'], expected_document['type'])
        self.assertEqual(hit['description'], expected_document['description'])

    def check_search_aggregations(
            self,
            counts: dict,
            expected_aggregations: dict):
        self.assertIn(
            'docCounts',
            counts,
            "counts dict should contain docCounts")
        self.assertIn(
            'buckets',
            expected_aggregations,
            "expected aggregations should contain buckets field")

        expected_aggs_count = 0
        for agg in expected_aggregations['buckets']:
            expected_aggs_count += agg['doc_count']

        numberOfResults = counts['numberOfResults']
        self.assertEqual(
            numberOfResults,
            expected_aggs_count,
            "number of results should match total in expected aggregations")
        # self.assertEqual(counts['docCounts'], expected_aggregations['buckets'])

        aggs = counts['docCounts']
        self.assertIsInstance(
            aggs, dict, "returned docCounts should be instance of dict")

        for bucket in expected_aggregations['buckets']:
            key = bucket['key']
            self.assertIn(key, aggs, "aggs should contain key '%s'" % key)
            self.assertEqual(
                bucket['doc_count'],
                aggs[key],
                "counts should be equal")

    def check_search_response(self, response, expected_keys: list):
        """
        Tests that search returns the correct json response
        :return:
        """
        # Make sure the structure of the response is correct
        json_data = response.json
        self.assertIsNotNone(json_data, "json data should not be none")
        self.assertIsInstance(
            json_data,
            dict,
            "json data should be instance of dict")

        # First, check all keys exist
        for k in expected_keys:
            self.assertIn(
                k,
                json_data,
                "json response does not contain key '%s'" %
                k)
            self.assertIsNotNone(
                json_data[k],
                "key '%s' should not be none" %
                k)

    def test_search(self):
        """
        Tests the standard ONS search endpoint
        :return:
        """
        from tests.server.search.dummy_documents import test_document, test_aggs

        target = "/search/conceptual/ons?q=%s" % self.search_term
        doc = test_document['_source']
        expected_keys = ['counts', 'featuredResult', 'result']

        request, response = self.post(target, 200)
        self.check_search_response(response, expected_keys)

        # Check the search results
        json_data = response.json
        self.check_search_result(json_data['result'], doc)

        # Test that aggregations were marshalled correctly
        self.check_search_aggregations(json_data['counts'], test_aggs)


if __name__ == "__main__":
    unittest.main()
