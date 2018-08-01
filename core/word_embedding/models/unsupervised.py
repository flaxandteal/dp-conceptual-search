from gensim.models.keyedvectors import Word2VecKeyedVectors
from numpy import ndarray


class UnsupervisedModel(object):
    def __init__(self, model: Word2VecKeyedVectors):
        self.model = model

        # Collect ranked list of words in vocab
        words = self.model.index2word

        w_rank = {}
        for i, word in enumerate(words):
            w_rank[word] = i
        self.words = w_rank

    def similar_by_vector(self, vector: ndarray, ret_sim=False, **kwargs):
        """
        Returns similar terms (and optionally, their similarity) to the given word vector.
        :param vector:
        :param ret_sim:
        :return:
        """
        if ret_sim:
            similar = [
                s for s in self.model.similar_by_vector(
                    vector, **kwargs)]
        else:
            similar = [s[0]
                       for s in self.model.similar_by_vector(vector, **kwargs)]
        return similar
