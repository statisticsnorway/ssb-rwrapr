import warnings
from numpy._typing import NDArray
import scipy
import rpy2.robjects as ro
import numpy as np
import pandas as pd

from types import NoneType
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Set, Tuple
from rpy2.robjects import FloatVector, pandas2ri, numpy2ri

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
def convert_py2r(args: List[Any], kwargs: Dict[str, Any]) -> None:
    for i, x in enumerate(args):
        args[i] = convert_pyobject2r(x)
    for k, v in kwargs.items():
        kwargs[k] = convert_pyobject2r(v)


def convert_pyobject2r(x: Any) -> Any: # RBaseObject | PyDtype | Any:
    from .RObject import RObject
    match x:
        case RObject():
            return x.Robj
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


def convert_numpy2r(x: NDArray) -> Any: # RBaseObject:
    if not x.shape:
        x = x[np.newaxis]
    match len(x.shape):
        case 0:
            raise ValueError("Unexpected shape of numpy array")
        case 1:
            return convert_numpy1D(x)
        case 2:
            return convert_numpy2D(x)
        case _:
            return convert_numpyND(x)

       
def convert_numpy1D(x: NDArray) -> Any: # RBaseObject:
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
                warnings.warn("dtype = object is not supported, this will probaly not work")
                y = convert_pyobject2r(x.tolist())
            finally:
                return ro.StrVector(y)
        case _:
            return x



def convert_numpy2D(x: NDArray) -> Any: # RBaseObject:
    flat_x: NDArray = x.flatten()
    nrow, ncol = x.shape
    y = convert_numpy1D(flat_x)
    f: Callable = ro.r("matrix")
    return f(y, nrow=nrow, ncol=ncol)


def convert_numpyND(x: NDArray) -> Any: # RBaseObject:
    flat_x: NDArray = x.flatten()
    dim: Tuple = x.shape
    y = convert_numpy1D(flat_x)
    f: Callable = ro.r("array")
    return f(y, dim = ro.IntVector(dim))


def dict2rlist(x: Dict | OrderedDict) -> ro.ListVector:
    return ro.ListVector({k: convert_pyobject2r(v) for k, v in x.items()})


def pylist2rlist(x: List | Tuple | Set) -> ro.ListVector:
    y: Dict[str, Any] = {str(k): v for k, v in enumerate(x)}
    unname: Callable = rcall("unname")
    return unname(dict2rlist(y))


def convert_pysparsematrix(x: scipy.sparse.coo_array | scipy.sparse.coo_matrix):
    try:
        sparseMatrix: Callable = rcall("Matrix::sparseMatrix")
        return sparseMatrix(i=ro.IntVector(x.row + 1),
                            j=ro.IntVector(x.col + 1),
                            x=ro.FloatVector(x.data),
                            dims=ro.IntVector(x.shape))
    except:
        return x


def pandas2r(x: pd.DataFrame) -> Any: # RBaseObject:
    return ro.DataFrame({k: convert_pyobject2r(x[k].to_numpy()) for k in x})

