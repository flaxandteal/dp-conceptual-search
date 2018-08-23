from tests.server.test_app import TestApp


class TestSpellChecker(TestApp):

    confidence_limit = 0.5

    expected = {
        "rpj": "rpi",
        "cph": "cpi",
        "murdr": "murder",
        "infltion": "inflation"
    }

    @property
    def query(self):
        tokens = self.expected.keys()
        return " ".join(tokens)

    def test_spell_checker(self):
        """
        Tests the spell checker API words for a select number of terms
        :return:
        """

        request, response = self.get(
            '/suggest/spelling?q=%s' %
            self.query, 200)

        json_result = response.json
        self.assertIsNotNone(json_result, "json result should not be None")
        self.assertIsInstance(
            json_result,
            dict,
            "json result should be instance of dict")

        tokens = self.query.split()

        for token in tokens:
            self.assertIn(
                token,
                json_result,
                "token '%s' should be in json response" %
                token)

            self.assertIn(
                'correction',
                json_result[token],
                "key 'correction' should be in entry for token '%s'" %
                token)

            self.assertIn('probability', json_result[token],
                          "key 'probability' should be in entry for token '%s'" % token)

            self.assertEqual(
                self.expected[token],
                json_result[token]['correction'])

            self.assertGreater(
                json_result[token]["probability"],
                self.confidence_limit,
                "confidence should be greater than %f" %
                self.confidence_limit)
