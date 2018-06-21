from enum import Enum
from gensim.models.keyedvectors import Word2VecKeyedVectors


class Models(Enum):
    ONS = "ons_supervised.vec"

    def __str__(self):
        return self.value


class UnsupervisedModel(object):
    def __init__(self, model: Word2VecKeyedVectors):
        self.model = model

        # Collect ranked list of words in vocab
        words = self.model.index2word

        w_rank = {}
        for i, word in enumerate(words):
            w_rank[word] = i
        self.words = w_rank