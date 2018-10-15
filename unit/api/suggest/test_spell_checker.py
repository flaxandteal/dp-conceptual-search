"""
Tests the suggest spell checker API
"""
from unit.utils.test_app import TestApp


class SpellCheckTestCase(TestApp):

    @property
    def sample_words(self) -> dict:
        """
        Returns a set of words to be used for testing, with their corrections
        :return:
        """
        return {
            "rpo": "rpi",
            "roi": "rpi",
            "cpl": "cpi",
            "infltion": "inflation",
            "economi": "economic"
        }

    def test_spell_check(self):
        """
        Mimics the unit test in the ml package, but directs requests through the API
        :return:
        """
        expected_keys = ["input_token", "correction", "probability"]
        sample_words = self.sample_words

        for sample_word in sample_words:
            params = {
                "q": sample_word,
            }
            url_encoded_params = self.url_encode(params)
            target = "/suggest/spelling?{0}".format(url_encoded_params)

            # Make the request
            request, response = self.get(target, 200)

            # Check the response
            self.assertTrue(hasattr(response, "json"), "response should have json data")
            data = response.json

            self.assertIsNotNone(data, "json data should not be none")
            self.assertIsInstance(data, list, "expected list, got {0}".format(type(data)))
            self.assertEqual(len(data), 1, "expected one result, got {0}".format(len(data)))

            suggestion = data[0]
            self.assertIsInstance(suggestion, dict, "expected dict, got {0}".format(type(suggestion)))

            for key in expected_keys:
                self.assertIn(key, suggestion, "suggestion should contain key '{0}'".format(key))

            self.assertEqual(suggestion['input_token'], sample_word, "expected input token {expected}, got {actual}"
                             .format(expected=sample_words, actual=suggestion['input_token']))

            self.assertEqual(suggestion['correction'], sample_words[sample_word],
                             "expected input token {expected}, got {actual}"
                             .format(expected=sample_words[sample_word], actual=suggestion['correction']))

            self.assertGreater(suggestion['probability'], 0.0, "expected probability > 0, got {0}"
                               .format(suggestion['probability']))

    def test_spell_check_empty_query(self):
        """
        Tests that a 400 BAD_REQUEST is raised for an empty query
        :return:
        """
        params = {
            "q": "",
        }
        url_encoded_params = self.url_encode(params)
        target = "/suggest/spelling?{0}".format(url_encoded_params)

        # Make the request and assert a 400 BAD_REQUEST response
        request, response = self.get(target, 400)

    def test_spell_check_no_tokens(self):
        """
        Tests that a 400 BAD_REQUEST is raised for a query with no input tokens (i.e whitespace)
        :return:
        """
        params = {
            "q": " ",
        }
        url_encoded_params = self.url_encode(params)
        target = "/suggest/spelling?{0}".format(url_encoded_params)

        # Make the request and assert a 400 BAD_REQUEST response
        request, response = self.get(target, 400)
