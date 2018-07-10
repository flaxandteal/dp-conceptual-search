import fastText
from sanic import Sanic

from server.sanic_extension import SanicExtension
from core.word_embedding.models.supervised import SupervisedModels, SupervisedModel


_models = {}


def load_model(model: SupervisedModels) -> SupervisedModel:
    if model in _models:
        return _models[model]
    raise RuntimeError("No model with name %s" % model)


class SanicFastText(SanicExtension):
    """
    Class to load/store .vec models
    """

    def init_app(self, app: Sanic, **kwargs) -> None:
        import os

        model_dir = app.config.get(
            "SUPERVISED_MODEL_DIR",
            "./supervised_models")

        for model_name in SupervisedModels:
            model_fname = os.path.normpath("%s/%s" % (model_dir, model_name))
            model = SupervisedModel(model_fname)

            _models[model_name] = model
