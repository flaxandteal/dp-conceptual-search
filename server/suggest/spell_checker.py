from server.word_embedding.sanic_word2vec import load_model
from server.word_embedding.models.unsupervised import Models, UnsupervisedModel


class SpellChecker(object):
    """
    Uses word embedding models to check the spelling of words and suggest corrections.
    """

    def __init__(self, model_name: Models):
        self.model_name = model_name
        self.model: UnsupervisedModel = load_model(self.model_name)

    @property
    def words(self):
        return self.model.words

    def correct_terms(self, terms):
        result = {}
        for term in terms:
            correction = self.correction(term)
            P = self.P(correction)
            if P > 0:
                result[term] = {"correction": correction, "P": P}
        return result

    def P(self, word):
        """ Probability of `word`. """
        # returns 0 if the word isn't in the dictionary
        if word not in self.words:
            return 0.
        return float(len(self.words)) / \
            (float(self.words.get(word, 0)) + float(len(self.words)))

    def correction(self, word):
        """ Most probable spelling correction for word. """
        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        """ Generate possible spelling corrections for word. """
        return self.known(
            [word]) or self.known(
            self.edits1(word)) or self.known(
            self.edits2(word)) or [word]

    def known(self, words):
        """ The subset of `words` that appear in the dictionary of WORDS. """
        return set(w for w in words if w in self.words)

    def edits1(self, word):
        """ All edits that are one edit away from `word`. """
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        """ All edits that are two edits away from `word`. """
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))
