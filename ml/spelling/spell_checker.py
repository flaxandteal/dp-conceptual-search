"""
Implementation of a spellchecker using word embedding models
"""
from typing import Generator, List
from ml.word_embedding.fastText.unsupervised import UnsupervisedModel


class SpeckCheckSuggestion(object):
    def __init__(self, input_token, correction, probability):
        self.input_token = input_token
        self.correction = correction
        self.probability = probability

    def to_dict(self) -> dict:
        return {
            "input": self.input_token,
            "correction": self.correction,
            "probability": self.probability
        }


class SpellChecker(object):
    """
    Uses word embedding models to check the spelling of words and suggest corrections.
    """

    def __init__(self, model: UnsupervisedModel):
        self.model: UnsupervisedModel = model

    @property
    def words(self) -> dict:
        return self.model.words

    def correct_terms(self, terms) -> List[SpeckCheckSuggestion]:
        """
        Returns a list of potential corrections, with their probabilities
        :param terms:
        :return:
        """
        result = []

        if not isinstance(terms, list):
            terms = [terms]
        for term in terms:
            correction = self.correction(term)
            P = self.P(correction)
            if P > 0:
                result.append(SpeckCheckSuggestion(term, correction, P))
        return result

    def P(self, word) -> float:
        """
        Probability of `word`.
        Returns 0 if the word isn't in the dictionary
        """
        if word not in self.words:
            return 0.
        return float(len(self.words)) / \
            (float(self.words.get(word, 0)) + float(len(self.words)))

    def correction(self, word) -> str:
        """ Most probable spelling correction for word. """
        return max(self.candidates(word), key=self.P)

    def candidates(self, word) -> set:
        """ Generate possible spelling corrections for word. """
        return self.known(
            [word]) or self.known(
            self.edits1(word)) or self.known(
            self.edits2(word)) or [word]

    def known(self, words) -> set:
        """ The subset of `words` that appear in the dictionary of WORDS. """
        return set(w for w in words if w in self.words)

    def edits1(self, word) -> set:
        """ All edits that are one edit away from `word`. """
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word) -> Generator:
        """ All edits that are two edits away from `word`. """
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))
