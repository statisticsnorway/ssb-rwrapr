import pandas as pd
import numpy as np
import scipy

import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
import rpy2.rlike.container as rcnt

from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, OrderedDict, Set, Tuple
from copy import Error
from rpy2.robjects import pandas2ri, numpy2ri, rpy2

from .nputils import np_collapse
from .lazy_rexpr import lazily, lazy_wrap
from .rutils import rcall


def convert_r2py(x: Any) -> Any:
    from .RObject import RObject
    from .RArray  import convert_numpy, is_valid_numpy, filter_numpy
    from .RDataFrame import convert_pandas, attempt_pandas_conversion, RDataFrame
    from .RList import convert_list, convert_dict, convert_rlist2py

    match x:
        case str() | int() | bool() | float():
            return x
        case rpy2.rinterface_lib.sexp.NULLType():
            return None
        case vc.DataFrame():
            return RDataFrame(x)
        case vc.Vector() | vc.Matrix() | vc.Array() if not is_rlist(x):
            return convert_numpy(x)
        case list():
            return convert_list(x)
        case tuple(): 
            return convert_list(x)
        case rcnt.OrdDict():
            return convert_dict(x, is_RDict=True)
        case dict():
            return convert_dict(x)
        case pd.DataFrame():
            return x
        case np.ndarray():
            if not is_valid_numpy(x):
                return attempt_pandas_conversion(x)
            return filter_numpy(x)
        case vc.ListSexpVector() | vc.ListVector():
            return convert_rlist2py(x)
        case _:
            return RObject(x)
