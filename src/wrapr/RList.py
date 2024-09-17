import numpy as np

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
        
# from .RObject import RObject
# from .RArray  import convert_numpy, is_valid_numpy, filter_numpy
# from .RDataFrame import convert_pandas, attempt_pandas_conversion, RDataFrame

class RList(np.ndarray):
    def __init__(self, Rdata):
        super().__init__()#convert_numpy(Rdata))
        self.Rattributes = None
    
    # def toR(self):
        # -> R-dataframe
        # -> R-Attributes -> convert to R
        # with_attributes: Callable = rcall("structure")
        # return with_attributes(R-dataframe, **R-Attributes) 

def convert_list(X: List | Tuple) -> Any:
    from .convert_r2py import convert_r2py
    out = [convert_r2py(x) for x in X]
    if isinstance(X, tuple):
        out = tuple(out)
    return out
       

def convert_rlist2py(X: vc.ListVector | vc.ListSexpVector) -> Any:
    from .RArray import convert_numpy
    names = convert_numpy(X.names)
    if names is not None and len(names):
        return convert_dict({n: x for n, x in zip(names, X)})
    else:
        return convert_list([x for x in X])


def is_rlist(X: Any) -> bool:
    match X:
        case vc.ListVector() | vc.ListSexpVector():
            return True
        case _:
            return False


def convert_dict(X: Dict | OrderedDict,
                 is_RDict: bool = False) -> Any:
    from .convert_r2py import convert_r2py
    try:
        # this needs to be improved considering named vectors
        if is_RDict and np.all(np.array(X.keys()) == None):
            Y = list(zip(*X.items()))[1]
            X = convert_r2py(Y)
        elif is_RDict:
            X = dict(X)

        for key in X:
            X[key] = convert_r2py(X[key])
    finally:
        return X
