import numpy as np


# Learning rate
def get_learning_rate() -> float:
    import os

    lr = float(os.environ.get("SEARCH_LEARNING_RATE", 0.25))
    return min(np.abs(lr), 1.0)


def default_distance_measure(
        original_vector: np.ndarray,
        term_vector: np.ndarray) -> np.ndarray:
    """
    Default method to measure distance between two vectors. Uses Euclidean distance.
    :param original_vector:
    :param term_vector:
    :return:
    """
    dist = term_vector - original_vector

    return dist


def default_move_session_vector(
        original_vector: np.ndarray,
        term_vector: np.ndarray,
        learning_rate: float=get_learning_rate()) -> np.ndarray:
    """
    Default method to modify a session vector to reflect interest in a term vector.
    :param original_vector: Word vector representing the present session.
    :param term_vector: Word vector representing the term of interest.
    :param learning_rate:
    :return: An updated word vector which has moved towards the term vector in the full N-dimensional
    vector space.
    """
    dist = default_distance_measure(original_vector, term_vector)

    new_vec = original_vector + (dist * learning_rate)
    return new_vec


def negative_move_session_vector(
        original_vector: np.ndarray,
        term_vector: np.ndarray) -> np.ndarray:
    """
    Default method to modify a session vector to reflect a negative interest in a term vector.
    :param original_vector: Word vector representing the present session.
    :param term_vector: Word vector representing the term of interest.
    :return: An updated word vector which has moved towards the term vector in the full N-dimensional
    vector space.
    """
    dist = default_distance_measure(original_vector, term_vector)

    new_vec = original_vector - (dist * get_learning_rate())
    return new_vec
