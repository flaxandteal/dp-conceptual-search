from .supervised_models_cache import get_supervised_model


def init_supervised_models(*args):
    """
    Performs a first-time load of all ML models specified
    :param args: series of filenames of models to initialise
    :return:
    """
    for arg in args:
        get_supervised_model(arg)
