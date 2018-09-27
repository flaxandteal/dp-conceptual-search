"""
Class for registering ML models
"""
from enum import Enum

from config.config_ml import UNSUPERVISED_MODEL_FILENAME


class Models(Enum):
    ONS_UNSUPERVISED_MODEL = UNSUPERVISED_MODEL_FILENAME
