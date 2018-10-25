"""
This file defines classes and methods for working with unsupervised fastText models.
We use the excellent gensim package for working with such models.
"""
from numpy import ndarray
from gensim.models.keyedvectors import Word2VecKeyedVectors


class UnsupervisedModel(object):
    def __init__(self, filename: str):
        self.model = Word2VecKeyedVectors.load_word2vec_format(filename)

        # Collect ranked list of words in vocab
        words = self.model.index2word

        w_rank = {}
        for i, word in enumerate(words):
            w_rank[word] = i
        self.words = w_rank

    def word_vec(self, word: str, use_norm=False) -> ndarray:
        """
        Returns the word vector for the given word
        :param word: Desired word to return vector for
        :param use_norm: Return normalised vector
        :return:
        """
        return self.model.word_vec(word, use_norm=use_norm)

    def similar_by_word(self, word: str, top_n: int=10, return_similarity=False, **kwargs) -> list:
        """
        Returns similar terms (and optionally, their similarity) to the given word.
        :param word: Word for which to search for similarities to
        :param top_n: Return the top_n similar words
        :param return_similarity: Return the similarity score with each word
        :param kwargs: Additional arguments
        :return:
        """
        word_vector = self.model.word_vec(word)
        return self.similar_by_vector(word_vector, top_n=top_n, return_similarity=return_similarity, **kwargs)

    def similar_by_vector(self, vector: ndarray, top_n: int=10, return_similarity=False, **kwargs) -> list:
        """
        Returns similar terms (and optionally, their similarity) to the given word vector.
        :param vector: Word vector for which to search for similarities to
        :param top_n: Return the top_n similar words
        :param return_similarity: Return the similarity score with each word
        :param kwargs: Additional arguments
        :return:
        """
        if return_similarity:
            similar = [
                s for s in self.model.similar_by_vector(
                    vector, topn=top_n, **kwargs)]
        else:
            similar = [s[0]
                       for s in self.model.similar_by_vector(vector, topn=top_n, **kwargs)]
        return similar
