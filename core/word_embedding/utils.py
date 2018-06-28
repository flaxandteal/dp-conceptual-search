import base64
import numpy as np
from numpy.linalg import norm

from typing import List

dbig = np.dtype('>f8')


def decode_float_list(base64_string) -> List[float]:
    bytes = base64.b64decode(base64_string)
    return np.frombuffer(bytes, dtype=dbig).tolist()


def encode_array(arr) -> str:
    base64_str = base64.b64encode(np.array(arr).astype(dbig)).decode("utf-8")
    return base64_str


def cosine_sim(vec1, vec2) -> float:
    """
    Computes the cosine similarity between two vectors
    :param vec1:
    :param vec2:
    :return:
    """
    cos_sim = np.dot(vec1, vec2) / \
        (norm(vec1) * norm(vec2))
    return cos_sim


def cosine_sim_matrix(matrix, vec) -> np.ndarray:
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
