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

from .RDataFrame import convert_pandas, attempt_pandas_conversion
from .RArray import convert_numpy, is_valid_numpy, filter_numpy


class Robject():
    def __init__(self, Robj: Any):
        self.Robj = Robj

    def __str__(self) -> str:
        # return captureRprint(self.Robj) 
        return self.Robj.__str__()

    def __repr__(self):
        # return self.Robj.__repr__()
        return self.Robj.__str__()

    def __getattr__(self, name: str) -> Any:
        fun: Callable = rfunc(name)
        return fun(self.Robj)

    def __getitem__(self, *args):
        return self.Robj.__getitem__(*args)

    def __iter__(self):
        return self.Robj.__iter__()

    def to_py(self):
        return convert_r2py(self.Robj)


def convert_r2py(x: Any) -> Any:
    match x:
        case str() | int() | bool() | float():
            return x
        case rpy2.rinterface_lib.sexp.NULLType():
            return None
        case vc.DataFrame():
            return convert_pandas(x)
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
            return Robject(x)
        

def convert_list(X: List | Tuple) -> Any:
    out = [convert_r2py(x) for x in X]
    if isinstance(X, tuple):
        out = tuple(out)
    return out
       

def convert_rlist2py(X: vc.ListVector | vc.ListSexpVector) -> Any:
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
