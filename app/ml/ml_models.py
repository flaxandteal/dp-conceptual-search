"""
Class for registering ML models
"""
from enum import Enum

from config import CONFIG


class Models(Enum):
    ONS_UNSUPERVISED_MODEL = CONFIG.ML.unsupervised_model_filename
