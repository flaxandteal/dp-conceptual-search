import os
from enum import Enum
from sanic import Sanic

from server.sanic_extension import SanicExtension

from core.word_embedding.models.supervised import SupervisedModel


_models = {}


class SupervisedModels(Enum):
    ONS = os.environ.get("ONS_SUPERVISED_MODEL_NAME", "ons_supervised.bin")

    def __str__(self):
        return self.value


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
        from sanic.log import logger

        model_dir = app.config.get(
            "SUPERVISED_MODEL_DIR",
            "./supervised_models")

        for model_name in SupervisedModels:
            logger.info("Loading supervised fastText model '%s'" % model_name)

            model_fname = os.path.normpath("%s/%s" % (model_dir, model_name))

            if os.path.isfile(model_fname):
                model = SupervisedModel(model_fname)

                num_words = len(model.get_words())
                num_labels = len(model.get_labels())
                dimension = model.get_dimension()
                logger.info(
                    "Loaded supervised fastText model '%s' with input/output matrix dimensions: (%d, %d)/(%d, %d)" %
                    (model_name, num_words, dimension, num_labels, dimension))

                _models[model_name] = model
            else:
                from sanic.log import logger
                message = "Unable to locate supervised model with filename '%s'" % model_fname
                logger.error(message)
                raise FileNotFoundError(message)
