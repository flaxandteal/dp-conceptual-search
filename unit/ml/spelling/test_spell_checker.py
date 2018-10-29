"""
Tests the custom spell checker class
"""
from unittest import TestCase

from dp_conceptual_search.config import CONFIG
from dp_conceptual_search.ml.spelling.spell_checker import SpellChecker
from dp_conceptual_search.ml.word_embedding.fastText.unsupervised import UnsupervisedModel


class SpellCheckerTestCase(TestCase):

    def setUp(self):
        """
        Initialise the default model
        :return:
        """
        model = UnsupervisedModel(CONFIG.ML.unsupervised_model_filename)
        self.spell_checker: SpellChecker = SpellChecker(model)

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

    def test_spelling_most_probable(self):
        """
        Tests that the spell checker returns the correct suggestions for a test sample of words
        :return:
        """
        sample_words = self.sample_words

        for key in sample_words:
            correction = self.spell_checker.correction(key)
            self.assertEqual(correction, sample_words[key], "expected {expected} for key {key}, but got {actual}"
                             .format(
                                 expected=sample_words[key],
                                 key=key,
                                 actual=correction
                             ))

    def test_spelling_correct_terms(self):
        """
        Tests that the spell checker returns the correct suggestions for a test sample of words
        :return:
        """
        sample_words = self.sample_words
        keys = list(sample_words.keys())

        corrections = self.spell_checker.correct_spelling(keys)
        for correction in corrections:
            self.assertEqual(correction.correction, sample_words[correction.input_token],
                             "expected {expected} for key {key}, but got {actual}".format(
                                 expected=sample_words[correction.input_token],
                                 key=correction.input_token,
                                 actual=correction.correction
                             ))
