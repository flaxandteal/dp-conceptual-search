from tests.server.test_app import TestApp


class TestSpellChecker(TestApp):

    confidence_limit = 0.5

    expected_keys = ['input_token', 'correction', 'probability']

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
            list,
            "json result should be instance of list")

        input_tokens = self.query.split()

        for entry in json_result:
            # Assert entry has correct keys
            for key in entry.keys():
                self.assertIn(key, self.expected_keys)
            # Assert input token is in list
            input_token = entry['input_token']

            self.assertIn(input_token, input_tokens)

            # Assert suggested correction is correct
            self.assertEqual(entry['correction'], self.expected[input_token])
