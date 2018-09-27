"""
ML specific configs
"""
import os

SUPERVISED_MODEL_FILENAME = os.environ.get("SUPERVISED_MODEL_FILENAME",
                                           "./unit/ml/test_data/supervised_models/ons_supervised.bin")

UNSUPERVISED_MODEL_FILENAME = os.environ.get("UNSUPERVISED_MODEL_FILENAME",
                                             "./ml/data/word2vec/ons_supervised.vec")
