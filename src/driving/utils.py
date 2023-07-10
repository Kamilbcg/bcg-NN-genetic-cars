import numpy as np


def randfloat(lower, upper):
    x = np.random.rand()
    return x * (upper - lower) + lower
