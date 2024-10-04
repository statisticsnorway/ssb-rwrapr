import warnings
from collections import OrderedDict
from collections.abc import Callable
from types import NoneType
from typing import Any

import numpy as np
import pandas as pd
import rpy2.robjects as ro
import scipy
import numpy.typing as npt

from .rutils import rcall

# We can uncomment this when we transition to 3.12
# type RBaseObject = (
#         ro.FloatVector | ro.FloatVector | ro.IntVector |
#         ro.ListVector | ro.Array | ro.FactorVector |
#         ro.Matrix | ro.BoolVector | ro.StrVector
#     )
#
# type PyDtype = (int | bool | str | float)


# functions for converting from py 2 R -----------------------------------------
def convert_py_args2r(args: list[Any], kwargs: dict[str, Any]) -> None:
    for i, x in enumerate(args):
        args[i] = convert_py2r(x)
    for k, v in kwargs.items():
        kwargs[k] = convert_py2r(v)


def convert_py2r(x: Any) -> Any:  # RBaseObject | PyDtype | Any:
    from .RArray import RArray
    from .RDataFrame import RDataFrame
    from .RDataFrame import pandas2r
    from .RFactor import RFactor
    from .RList import RDict
    from .RList import RList
    from .RList import dict2rlist
    from .RList import pylist2rlist
    from .RView import RView

    match x:
        case RView() | RArray() | RList() | RDataFrame() | RDict() | RFactor():
            return x.toR()
        case np.ndarray():
            return convert_numpy2r(x)
        case scipy.sparse.coo_array() | scipy.sparse.coo_matrix():
            return convert_pysparsematrix(x)
        case OrderedDict() | dict():
            return dict2rlist(x)
        case list() | tuple() | set():
            return pylist2rlist(x)
        case pd.DataFrame():
            return pandas2r(x)
        case pd.Categorical():
            return ro.FactorVector(x)
        case pd.Series():
            return convert_py2r(x.to_numpy())
        case NoneType():
            return ro.NULL
        case np.bool_():
            return bool(x)
        case np.int8() | np.int16() | np.int32() | np.int64():
            return int(x)
        case np.float16() | np.float32() | np.float64():
            return float(x)
        case np.str_() | np.bytes_():
            return str(x)
        case _:
            return x


def convert_numpy2r(x: npt.NDArray) -> Any:  # RBaseObject:
    y = x.copy()
    if not y.shape:
        y = y[np.newaxis]
    match len(y.shape):
        case 0:
            raise ValueError("Unexpected shape of numpy array")
        case 1:
            return convert_numpy1D(y)
        case 2:
            return convert_numpy2D(y)
        case _:
            return convert_numpyND(y)


def convert_numpy1D(x: npt.NDArray) -> Any:  # RBaseObject:
    match x.dtype.kind:
        case "b":
            return ro.BoolVector(x)
        case "i":
            return ro.IntVector(x)
        case "f":
            return ro.FloatVector(x)
        case "U" | "S":
            return ro.StrVector(x)
        case "O":
            try:
                y = x.astype("U")
            except:
                warnings.warn(
                    "dtype = object is not supported, this will probaly not work"
                )
                y = convert_py2r(x.tolist())
            finally:
                return ro.StrVector(y)
        case _:
            return x


def convert_numpy2D(x: npt.NDArray) -> Any:  # RBaseObject:
    flat_x: NDArray = x.flatten(order="F")
    nrow, ncol = x.shape
    y = convert_numpy1D(flat_x)
    f: Callable = ro.r("matrix")
    return f(y, nrow=nrow, ncol=ncol)


def convert_numpyND(x: npt.NDArray) -> Any:  # RBaseObject:
    flat_x: NDArray = x.flatten(order="F")
    dim: tuple = x.shape
    y = convert_numpy1D(flat_x)
    f: Callable = ro.r("array")
    return f(y, dim=ro.IntVector(dim))


def convert_pysparsematrix(x: scipy.sparse.coo_array | scipy.sparse.coo_matrix):
    try:
        sparseMatrix: Callable = rcall("Matrix::sparseMatrix")
        return sparseMatrix(
            i=ro.IntVector(x.row + 1),
            j=ro.IntVector(x.col + 1),
            x=ro.FloatVector(x.data),
            dims=ro.IntVector(x.shape),
        )
    except:
        return x


# def pandas2r(x: pd.DataFrame) -> Any:  # RBaseObject:
#     return ro.DataFrame({k: convert_py2r(x[k].to_numpy()) for k in x})
