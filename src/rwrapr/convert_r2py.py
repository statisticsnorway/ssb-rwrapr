from typing import Any

import numpy as np
import pandas as pd
import rpy2.rlike.container as rcnt
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.rinterface_lib.sexp import NULLType

from .rdataframe import RDataFrame
from .rdataframe import attempt_pandas_conversion
from .rfactor import RFactor
from .rlist import convert_r2pydict
from .rlist import convert_r2pylist
from .rlist import convert_rlist2py
from .rlist import is_rlist
from .rutils import has_unsupported_rclass
from .rutils import is_na
from .rview import RView
from .rview import convert_s4


# TODO: Consider changing return type hint to union of possible types
def convert_r2py(x: Any, ignore_s3_s4: bool = False) -> Any:
    # Need to import these here to avoid circular imports
    from .rarray import filter_numpy
    from .rarray import get_rarray
    from .rarray import is_valid_numpy

    match x:
        case str() | int() | bool() | float():
            return x
        case NULLType():
            return None
        case _ if is_na(x):
            return (
                np.nan
            )  # this should probably be reconsidered at some point (see line 35 in renv.py)
        case vc.DataFrame():
            return RDataFrame(x)
        case vc.FactorVector():
            return RFactor(x)
        case vc.Vector() | vc.Matrix() | vc.Array() if not is_rlist(x):
            return get_rarray(x)  # return RArray, or int|str|bool|float if len == 1
        case ro.methods.RS4():
            return convert_s4(x, ignore_s4=ignore_s3_s4)
        case _ if has_unsupported_rclass(x) and not ignore_s3_s4:
            return RView(x)
        case list():
            return convert_r2pylist(x)
        case tuple():
            return convert_r2pylist(x)
        case rcnt.OrdDict():
            return convert_r2pydict(x, is_rdict=True)
        case dict():
            return convert_r2pydict(x)
        case pd.DataFrame():
            return x
        case np.ndarray():
            if not is_valid_numpy(x):
                return attempt_pandas_conversion(x)
            return filter_numpy(x, flatten=True)
        case vc.ListSexpVector() | vc.ListVector():
            return convert_rlist2py(x)
        case _:
            return RView(x)
