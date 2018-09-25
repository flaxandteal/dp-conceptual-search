"""
This file defines classes and methods for working with supervised fastText models.
We use the excellent gensim package for working with such models.
"""
from numpy import ndarray
from gensim.models.keyedvectors import Word2VecKeyedVectors


class UnsupervisedModel(object):
    def __init__(self, model: Word2VecKeyedVectors):
        self.model = model

        # Collect ranked list of words in vocab
        words = self.model.index2word

        w_rank = {}
        for i, word in enumerate(words):
            w_rank[word] = i
        self.words = w_rank

    def word_vec(self, word: str, use_norm=False) -> ndarray:
        """
        Returns the word vector for the given word
        :param word:
        :param use_norm: Return normalised vector
        :return:
        """
        return self.model.word_vec(word, use_norm=use_norm)

    def similar_by_word(self, word: str, topn: int=10, ret_sim=False, **kwargs) -> list:
        """
        Returns similar terms (and optionally, their similarity) to the given word.
        :param word:
        :param topn:
        :param ret_sim:
        :param kwargs:
        :return:
        """
        word_vector = self.model.word_vec(word)
        return self.similar_by_vector(word_vector, topn=topn, ret_sim=ret_sim, **kwargs)

    def similar_by_vector(self, vector: ndarray, topn: int=10, ret_sim=False, **kwargs) -> list:
        """
        Returns similar terms (and optionally, their similarity) to the given word vector.
        :param vector:
        :param topn:
        :param ret_sim:
        :return:
        """
        if ret_sim:
            similar = [
                s for s in self.model.similar_by_vector(
                    vector, topn=topn, **kwargs)]
        else:
            similar = [s[0]
                       for s in self.model.similar_by_vector(vector, topn=topn, **kwargs)]
        return similar
