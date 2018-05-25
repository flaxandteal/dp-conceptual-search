import unittest
from server.word_embedding.supervised_models import init, load_model, SupervisedModels


class TestSupervisedModels(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSupervisedModels, self).__init__(*args, **kwargs)

        init()
        self.model = load_model(SupervisedModels.ONS)

    def test_cosine_sim(self):
        """
        Test the cosine similarity between two vectors
        :return:
        """
        from server.word_embedding.utils import cosine_sim

        u = self.model.get_word_vector("homicide")
        v = self.model.get_word_vector("murder")

        sim = cosine_sim(u, v)
        self.assertAlmostEqual(sim, 0.85451025, 5)

    def test_embedding_vector(self):
        """
        Define an embedding vector close to that of homicide and test cosine sim
        :return:
        """
        import numpy as np
        from server.word_embedding.utils import decode_float_list, cosine_sim

        embedding_vector = "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"
        embedding_vector = np.array(decode_float_list(embedding_vector))

        homicide = self.model.get_word_vector("homicide")

        sim = cosine_sim(homicide, embedding_vector)

        self.assertAlmostEqual(sim, 0.99999, 3)
