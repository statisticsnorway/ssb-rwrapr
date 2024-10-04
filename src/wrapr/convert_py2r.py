import warnings
from numpy._typing import NDArray
import scipy
import rpy2.robjects as ro
import numpy as np
import pandas as pd

from types import NoneType
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Tuple

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
def convert_py_args2r(args: List[Any], kwargs: Dict[str, Any]) -> None:
    for i, x in enumerate(args):
        args[i] = convert_py2r(x)
    for k, v in kwargs.items():
        kwargs[k] = convert_py2r(v)


def convert_py2r(x: Any) -> Any:  # RBaseObject | PyDtype | Any:
    from .RView import RView
    from .RArray import RArray, convert_numpy2r
    from .RList import RList, RDict, pylist2rlist, dict2rlist
    from .RFactor import RFactor
    from .RDataFrame import RDataFrame, pandas2r
    from .sparse import convert_pysparsematrix

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
        case np.int_() | np.int8() | np.int16() | np.int32() | np.int64():
            return int(x)
        case np.int_() | np.float16() | np.float32() | np.float64():
            return float(x)
        case np.str_() | np.bytes_():
            return str(x)
        case _:
            return x
