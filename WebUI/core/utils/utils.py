import numpy as np


def flatten(ls):
    """
    Flattens a list of list into a single list
    input ls, List of Lists
    output list
    """

    return [item for sublist in ls for item in sublist]


def first_last_nonzero(arr, axis, invalid_val=-1):
    """
    Fast search for the first and last values in each column that isn't zero.
    """
    mask = arr != 0
    val = arr.shape[axis] - np.flip(mask, axis=axis).argmax(axis=axis) - 1

    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val), np.where(
        mask.any(axis=axis), val, invalid_val
    )
