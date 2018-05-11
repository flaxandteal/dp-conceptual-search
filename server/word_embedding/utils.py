import numpy as np


def cosine_sim(vec1, vec2):
    """
    Computes the cosine similarity between two vectors
    :param vec1:
    :param vec2:
    :return:
    """
    cos_sim = np.dot(vec1, vec2) / \
        (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return cos_sim


def cosine_sim_matrix(matrix, vec):
    """
    Computes the cosine similarities between a matrix and a vector
    :param matrix:
    :param vec:
    :return:
    """
    # cos_sim is array like
    cos_sim = np.dot(matrix, vec) / \
        (np.linalg.norm(matrix, axis=1) * np.linalg.norm(vec))
    return cos_sim
