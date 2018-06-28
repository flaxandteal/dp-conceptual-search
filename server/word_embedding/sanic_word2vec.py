import gensim
from sanic import Sanic

from server.sanic_extension import SanicExtension
from core.word_embedding.models.unsupervised import Models, UnsupervisedModel


_models = {}


def load_model(model: Models) -> UnsupervisedModel:
    if model in _models:
        return _models[model]
    raise RuntimeError("No model with name %s" % model)


class SanicWord2Vec(SanicExtension):
    """
    Class to load/store .vec models
    """

    def init_app(self, app: Sanic, **kwargs) -> None:
        import os

        model_dir = app.config.get("WORD2VEC_MODEL_DIR", "./word2vec")

        for model_name in Models:
            model_fname = os.path.normpath("%s/%s" % (model_dir, model_name))
            model = gensim.models.KeyedVectors.load_word2vec_format(
                model_fname)

            _models[model_name] = UnsupervisedModel(model)
