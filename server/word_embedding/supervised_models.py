import enum
import fastText
import numpy as np
from .utils import cosine_sim, cosine_sim_matrix

_models = {}


class SupervisedModels(enum.Enum):
    ONS = "ons_supervised.bin"

    def __str__(self):
        return self.value


def norm(vec):
    return np.linalg.norm(vec, axis=0)


class SupervisedModel(object):
    def __init__(self, supervised_model, prefix="__label__"):
        assert isinstance(supervised_model, fastText.FastText._FastText)
        self.f = supervised_model
        self.prefix = prefix

        # Normalised vectors
        # self.input_matrix_normalised = self._normalise_matrix(
        #     self.f.get_input_matrix())
        self.output_matrix_normalised = self._normalise_matrix(
            self.f.get_output_matrix())

        # Labels
        self.labels = np.array([l.replace(self.prefix, "")
                                for l in self.f.get_labels()])

    @staticmethod
    def _normalise_matrix(matrix):
        norm_vector = np.linalg.norm(matrix, axis=1)
        normed_matrix = np.zeros(matrix.shape)

        for i in range(len(matrix)):
            normed_matrix[i] = matrix[i] / norm_vector[i]
        return normed_matrix

    def get_sentence_vector(self, sentence):
        """
        Wraps fastText.get_sentence_vector and calls lower on the input sentence
        :param sentence:
        :return:
        """
        vec = self.f.get_sentence_vector(sentence.lower())
        return vec / norm(vec)

    def get_word_vector(self, word):
        """
        Returns the word vector for this word.
        :param word:
        :return:
        """
        vec = self.f.get_word_vector(word)
        return vec / norm(vec)

    def get_label_vector(self, label):
        """
        Returns the word vector for this label.
        :param label:
        :return:
        """
        if label.startswith(self.prefix) is False:
            label = "%s%s" % (self.prefix, label)

        if label in self.labels:
            ix = np.where(self.labels == label)
            vec = self.f.get_output_matrix()[ix][0]
            return vec / norm(vec)
        return np.zeros(self.f.get_dimension())

    @staticmethod
    def _get_index_for_vector(matrix, vector):
        cosine_similarity = cosine_sim_matrix(matrix, vector)
        ix = np.abs(cosine_similarity - cosine_similarity.max()).argmin()

        return cosine_similarity, ix

    @staticmethod
    def _get_top_n(words, cosine_similarity, ind, top_n):
        top_n_words = words[ind][:top_n]
        top_n_similarity = cosine_similarity[ind][:top_n]
        return top_n_words, top_n_similarity

    # def get_words_for_vector(self, vector, top_n=1):
    #     """
    #     Returns the word(s) nearest to the given vector
    #     :param vector:
    #     :param top_n:
    #     :return:
    #     """
    #     cosine_similarity = cosine_sim_matrix(self.input_matrix_normalised, vector)
    #     ind = np.argsort(-cosine_similarity)
    #
    #     words = self.f.get_words()
    #     return self._get_top_n(words, cosine_similarity, ind, top_n)

    def get_labels_for_vector(self, vector, top_n=1):
        """
        Returns the label(s) nearest to the given vector
        :param vector:
        :param top_n:
        :return:
        """
        cosine_similarity = cosine_sim_matrix(
            self.output_matrix_normalised, vector)
        ind = np.argsort(-cosine_similarity)

        return self._get_top_n(self.labels, cosine_similarity, ind, top_n)

    def keywords(self, text, top_n=10):
        labels, proba = self.f.predict(text, top_n)

        # Clean up labels
        labels = [
            label.replace(
                self.prefix,
                "") if self.prefix in label else label for label in labels]

        result = [{"label": label, "P": P} for label, P in zip(labels, proba)]

        # Sort by probability
        result = sorted(result, key=lambda item: item["P"], reverse=True)
        return result

    def similarity_by_word(self, word1, word2):
        """
        :param word1:
        :param word2:
        :return:
        """
        vec1 = self.get_word_vector(word1)
        vec2 = self.get_word_vector(word2)
        return self.similarity_by_vector(vec1, vec2)

    @staticmethod
    def similarity_by_vector(vec1, vec2):
        """
        :param vec1:
        :param vec2:
        :return:
        """
        return cosine_sim(vec1, vec2)


def init():
    import os

    supervised_model_dir = os.getenv(
        "SUPERVISED_MODEL_DIR",
        "./supervised_models")
    for model_name in SupervisedModels:
        fname = "%s/%s" % (supervised_model_dir, model_name)
        if os.path.isfile(fname):
            model = fastText.load_model(fname)
            _models[model_name] = SupervisedModel(model)


def load_model(model_name: SupervisedModels) -> SupervisedModel:
    if model_name in _models:
        return _models[model_name]
    raise RuntimeError("No model with name %s" % model_name)
