import numpy as np
from numpy.typing import NDArray
from rpy2.rlike.container import Any


def np_contains(x: NDArray, pattern=Any):
    return np.any(x == pattern)


def np_collapse(x: NDArray[str], sep="_") -> str:
    if not x.shape:
        x = x[np.newaxis]
    return sep.join(x)
