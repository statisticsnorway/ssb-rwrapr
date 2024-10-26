from collections import OrderedDict
from types import NoneType
from typing import Any
from typing import TypeAlias

import numpy as np
import pandas as pd
import rpy2.robjects as ro
import scipy  # type: ignore

from .rlist import RDict
from .rlist import RList
from .rlist import dict2rlist
from .rlist import pylist2rlist
from .rview import RView
from .sparse import convert_pysparsematrix


# We can uncomment this when we transition to 3.12
RBaseObject: TypeAlias = (
    ro.FloatVector
    | ro.IntVector
    | ro.ListVector
    | ro.Array
    | ro.FactorVector
    | ro.Matrix
    | ro.BoolVector
    | ro.StrVector
)

PyDtype: TypeAlias = int | bool | str | float


# functions for converting from py 2 R -----------------------------------------
def convert_py_args2r(args: list[Any], kwargs: dict[str, Any]) -> None:
    for i, x in enumerate(args):
        args[i] = convert_py2r(x)
    for k, v in kwargs.items():
        kwargs[k] = convert_py2r(v)


def convert_py2r(x: Any) -> RBaseObject | PyDtype | Any:
    # Need to import these here to avoid circular imports
    from .rarray import RArray
    from .rarray import convert_numpy2r
    from .rdataframe import RDataFrame
    from .rdataframe import pandas2r
    from .rfactor import RFactor

    match x:
        case RView() | RArray() | RList() | RDataFrame() | RDict() | RFactor():
            return x.to_r()
        case _ if x is np.nan:
            return (
                ro.NA_Logical
            )  # this should probably be reconsidered at some point (see line 35 in renv.py)
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
        case _ if np.isscalar(x):
            return np.asarray(
                x
            ).item()  # x.item() should work, but will give a linter error
        case _:
            return x
