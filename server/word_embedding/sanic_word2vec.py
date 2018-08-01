import os
import gensim
from enum import Enum
from sanic import Sanic

from server.sanic_extension import SanicExtension

from core.word_embedding.models.unsupervised import UnsupervisedModel


_models = {}


class Models(Enum):
    ONS = os.environ.get("ONS_W2V_MODEL_NAME", "ons_supervised.vec")

    def __str__(self):
        return self.value


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
