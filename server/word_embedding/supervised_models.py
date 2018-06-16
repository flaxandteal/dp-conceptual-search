import enum
import fastText
import numpy as np
from server.word_embedding.utils import cosine_sim, cosine_sim_matrix

_models = {}


class SupervisedModels(enum.Enum):
    ONS = "ons_supervised.bin"

    def __str__(self):
        return self.value


class SupervisedModel(fastText.FastText._FastText):
    def __init__(self, model: str, prefix: str="__label__", **kwargs) -> None:
        super(SupervisedModel, self).__init__(model=model, **kwargs)

        self.prefix = prefix

        # Labels
        self.labels = np.array([l.replace(self.prefix, "")
                                for l in self.get_labels()])

    @staticmethod
    def _normalise_matrix(matrix):
        norm_vector = np.linalg.norm(matrix, axis=1)
        normed_matrix = np.zeros(matrix.shape)

        for i in range(len(matrix)):
            normed_matrix[i] = matrix[i] / norm_vector[i]
        return normed_matrix

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

    def predict(self, text, k=1, threshold=0.0):
        """
        Overwrites super method but removes prefix from labels
        :param text:
        :param k:
        :param threshold:
        :return:
        """
        labels, probabilities = super(
            SupervisedModel, self).predict(
            text, k=k, threshold=threshold)

        parsed_labels = []
        for label in labels:
            parsed_labels.append(label.replace(self.prefix, ""))

        return parsed_labels, probabilities

    def keywords(self, text, top_n=10):
        labels, proba = self.predict(text, k=top_n)

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
            _models[model_name] = SupervisedModel(fname)
        else:
            raise RuntimeError(
                "Unable to locate supervised model file: %s" %
                fname)


def load_model(model_name: SupervisedModels) -> SupervisedModel:
    if model_name in _models:
        return _models[model_name]
    raise RuntimeError("No model with name %s" % model_name)
