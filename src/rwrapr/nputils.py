import numpy as np
from numpy.typing import NDArray
from rpy2.rlike.container import Any


def np_contains(x: NDArray[Any], pattern: Any) -> np.bool_:
    return np.any(x == pattern)


def np_collapse(x: NDArray[np.str_], sep: str = "_") -> str:
    if not x.shape:
        x = x[np.newaxis]
    return sep.join(x)
