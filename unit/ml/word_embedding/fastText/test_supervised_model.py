"""
Tests our SupervisedModel class
"""
from os.path import isfile
from unittest import TestCase

from config import CONFIG
from ml.word_embedding.fastText.supervised import SupervisedModel


class SupervisedModelTestCase(TestCase):
    def setUp(self):
        """
        Initialise the default model
        :return:
        """
        fname = CONFIG.ML.supervised_model_filename
        self.assertTrue(isfile(fname),
                        "must be able to locate default model at path {0}".format(fname))

        self.model = SupervisedModel(filename=fname)

    def test_predict(self):
        """
        Test the predict method returns the correct number of predictions, with the label prefix removed
        :return:
        """
        k = 10
        threshold = 0.0
        parsed_labels, probabilities = self.model.predict("rpi", k=k, threshold=threshold)

        self.assertEqual(len(parsed_labels), k,
                         "expected {k} parsed_results, got {actual}".format(k=k, actual=len(parsed_labels)))
        self.assertEqual(len(probabilities), k,
                         "expected {k} probabilities, got {actual}".format(k=k, actual=len(probabilities)))

        # Assert model label prefix isn't in parsed_labels
        for parsed_label in parsed_labels:
            self.assertNotIn(parsed_label, self.model.label_prefix, "prefix '{0}' should not be in parsed label '{1}'"
                             .format(self.model.label_prefix, parsed_label))

    def test_cosine_similarity(self):
        """
        Tests that the cosine similarity between the words 'murder' and 'homicide' is greater than a given threshold
        :return:
        """
        # First, try similarity_by_word
        word1 = "murder"
        word2 = "homicide"
        threshold = 0.5  # arbitrary 'good' score
        similarity = self.model.similarity_by_word(word1, word2)

        self.assertGreater(similarity, threshold,
                           "similarity between words '{word1}' and '{word2}' should be greater than {threshold}"
                           .format(word1=word1, word2=word2, threshold=threshold))

        # Test similar_by_vector gives same answer
        vector1 = self.model.get_word_vector(word1)
        vector2 = self.model.get_word_vector(word2)

        similar_by_vector = self.model.similarity_by_vector(vector1, vector2)

        self.assertEqual(similarity, similar_by_vector, "similar_by_word and similar_by_vector should give same answer")

