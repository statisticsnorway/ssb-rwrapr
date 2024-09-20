from copy import Error
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import OrderedDict
from typing import Set
from typing import Tuple

import numpy as np
import pandas as pd
import rpy2.rlike.container as rcnt
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
import scipy
from numpy.typing import NDArray
from rpy2.robjects import numpy2ri
from rpy2.robjects import pandas2ri
from rpy2.robjects import rpy2


from .nputils import np_collapse
from .lazy_rexpr import lazily, lazy_wrap
from .rutils import has_unsupported_rclass, rcall


def convert_r2py(x: Any, ignoreS3: bool = False) -> Any:
    from .RArray import get_RArray, filter_numpy, is_valid_numpy
    from .RDataFrame import RDataFrame
    from .RDataFrame import attempt_pandas_conversion
    from .RList import convert_r2pydict
    from .RList import convert_r2pylist
    from .RList import convert_rlist2py
    from .RList import is_rlist
    from .RView import RView, convert_s4


    match x:
        case str() | int() | bool() | float():
            return x
        case rpy2.rinterface_lib.sexp.NULLType():
            return None
        case vc.DataFrame():
            return RDataFrame(x)
        case vc.Vector() | vc.Matrix() | vc.Array() if not is_rlist(x):
            # return convert_numpy(x)
            return get_RArray(x) # return RArray, or int|str|bool|float if len == 1
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
