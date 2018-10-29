"""
This file defines useful utility methods for working with word vectors
"""
import base64
from typing import List

import inflect
import numpy as np
from numpy.linalg import norm
from nltk.corpus import stopwords

# Define constants
_stops = stopwords.words("english")  # dictionary of English stop words
_inflect_engine = inflect.engine()  # engine to convert nouns -> singulars


def clean_string(text: str):
    """
    Removes non alpha-numeric chars from a string
    :param text:
    :return:
    """
    import re

    s = re.sub("[^a-zA-Z ]", "", text).lower()
    return s


def replace_nouns_with_singulars(text: str):
    """
    Removes nouns from a string and replaces them with their equivalent singulars
    :param text:
    :return:
    """
    tokens = text.split()

    singulars = []
    for t in tokens:
        singular = _inflect_engine.singular_noun(t)
        if singular:
            singulars.append(singular)
        else:
            singulars.append(t)

    s = " ".join(singulars)

    return s


def remove_stop_words(text: str):
    """
    Removes stop words from a string
    :param text:
    :return:
    """
    tokens = [t for t in text.split() if t not in _stops]

    return " ".join(tokens)


def decode_float_list(base64_string) -> List[float]:
    """
    Decodes a list of floats encoded as a binary string
    :param base64_string:
    :return:
    """
    # Decode to 8 byte floats (> = big-endian)
    float_8byte_big_endian = '>f8'

    decoded_bytes = base64.b64decode(base64_string)
    return np.frombuffer(decoded_bytes, dtype=np.dtype(float_8byte_big_endian)).tolist()


def encode_float_list(array: List[float]) -> str:
    """
    Encodes a list of floating point numbers as a binary string
    :param array:
    :return:
    """
    # Encode from 8 byte floats (> = big-endian)
    float_8byte_big_endian = '>f8'

    base64_str = base64.b64encode(np.array(array).astype(np.dtype(float_8byte_big_endian))).decode("utf-8")
    return base64_str


def cosine_similarity(vec1, vec2) -> np.float:
    """
    Computes the cosine similarity between two vectors
    :param vec1:
    :param vec2:
    :return:
    """
    cos_sim = np.dot(vec1, vec2) / \
        (norm(vec1) * norm(vec2))

    return cos_sim


def cosine_similarity_matrix(matrix, vec) -> np.ndarray:
    """
    Computes the cosine similarities between a matrix and a vector
    :param matrix:
    :param vec:
    :return:
    """
    # cos_sim is array like
    cos_sim = np.dot(matrix, vec) / \
        (norm(matrix, axis=1) * norm(vec))
    return cos_sim
