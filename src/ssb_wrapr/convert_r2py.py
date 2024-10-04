from typing import Any

import numpy as np
import pandas as pd
import rpy2.rlike.container as rcnt
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import rpy2

from .rutils import has_unsupported_rclass


def convert_r2py(x: Any, ignoreS3: bool = False) -> Any:
    from .RArray import filter_numpy
    from .RArray import get_RArray
    from .RArray import is_valid_numpy
    from .RDataFrame import RDataFrame
    from .RDataFrame import attempt_pandas_conversion
    from .RFactor import RFactor
    from .RList import convert_r2pydict
    from .RList import convert_r2pylist
    from .RList import convert_rlist2py
    from .RList import is_rlist
    from .RView import RView
    from .RView import convert_s4

    match x:
        case str() | int() | bool() | float():
            return x
        case rpy2.rinterface_lib.sexp.NULLType():
            return None
        case vc.DataFrame():
            return RDataFrame(x)
        case vc.FactorVector():
            return RFactor(x)
        case vc.Vector() | vc.Matrix() | vc.Array() if not is_rlist(x):
            # return convert_numpy(x)
            return get_RArray(x)  # return RArray, or int|str|bool|float if len == 1
        case ro.methods.RS4():
            return convert_s4(x)
        case _ if has_unsupported_rclass(x) and not ignoreS3:
            return RView(x)
        case list():
            return convert_r2pylist(x)
        case tuple():
            return convert_r2pylist(x)
        case rcnt.OrdDict():
            return convert_r2pydict(x, is_RDict=True)
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
