from collections.abc import Callable
from typing import Any

import numpy as np
import rpy2.robjects as ro
from numpy.typing import NDArray


supported_classes = {"list", "array", "matrix", "vector", "atomic"}


def rcall(expr: str) -> Any:
    return ro.r(expr, print_r_warnings=False, invisible=True)


def get_rclass(x: Any) -> NDArray[np.str_] | None:
    from .function_wrapper import rfunc

    try:
        f: Callable[..., Any] | Any = rfunc("class")
        return np.asarray(f(x), dtype="U")
    except Exception:
        return None


def has_unsupported_rclass(x: Any) -> bool:
    rclass: NDArray[np.str_] | Any = get_rclass(x)

    if rclass is None or len(rclass.tolist()) == 0:
        return False
    if isinstance(rclass.tolist(), str):
        rclass = {rclass.tolist()}
    else:
        rclass = set(rclass.tolist())

    return len(rclass) > 0 and not rclass.issubset(supported_classes)


def as_matrix(x: Any) -> NDArray[Any] | Any:
    from .function_wrapper import rfunc

    f: Callable[..., Any] | Any = rfunc("as.matrix")
    return f(x)


def is_na(x: Any) -> bool:
    return (
        x is ro.NA_Character
        or x is ro.NA_Integer
        or x is ro.NA_Real
        or x is ro.NA_Logical
        or x is ro.NA_Complex
    )
