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
    match x:
        case str() | int() | bool() | float():
            return x
        case rpy2.rinterface_lib.sexp.NULLType():
            return None
        case ro.methods.RS4():
            return convert_s4(x)
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
            return generic_conversion(x)
        

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


def convert_numpy(x: vc.Vector | NDArray) -> NDArray | None:
    if isinstance(x, rpy2.rinterface_lib.sexp.NULLType):
        return None
    match x: # this should be expanded upon
        case vc.BoolVector() | vc.BoolArray() | vc.BoolMatrix():
            dtype = "bool"
        case vc.FloatVector() | vc.FloatArray() | vc.FloatMatrix():
            dtype = "float"
        case vc.IntVector() | vc.IntArray() | vc.IntMatrix():
            dtype = "int"
        case vc.StrArray() | vc.StrVector() | vc.StrMatrix():
            dtype = "U"
        case _:
            dtype = None

    y = np.asarray(x, dtype=dtype)
    return filter_numpy(y)


def filter_numpy(x: NDArray) -> NDArray | int | str | float | bool:
    # sometimes a numpy array will have one element with shape (,)
    # this should be (1,)
    y = x[np.newaxis][0] if not x.shape else x
    # if shape is (1,) we should just return as int | str | float | bool
    # R doesn't have these types, only vectors/arrays, this will probably
    # give unexpected results for users who are unfamiliar with R, so
    # we return the first element instead
    y = y[0] if y.shape == (1,) else y
    return y


def is_valid_numpy(x: NDArray) -> bool:
    return x.dtype.fields is None


def convert_pandas(df: vc.DataFrame) -> pd.DataFrame:
    colnames = df.names
    df_dict = {c: convert_numpy(x) for c, x in zip(colnames, list(df))}
    return pd.DataFrame(df_dict) 

    with (ro.default_converter + pandas2ri.converter).context():
        pd_df = ro.conversion.get_conversion().rpy2py(df)
    return pd_df


def attempt_pandas_conversion(x: Any) -> Any:
    try: 
        return pd.DataFrame(x)
    except:
        return x


def generic_conversion(x: Any) -> Any:
    try:
        arr = np.asarray(x)
        if not is_valid_numpy(arr):
            raise Error
        return arr
    except: 
        return attempt_pandas_conversion(x)


def convert_s4(x: ro.methods.RS4) -> Any:
    rclass = get_rclass(x)
    if rclass is None:
        return generic_conversion(x)

    match np_collapse(rclass):
        case "dgCMatrix": # to do: put this in a seperate function
            dense = convert_numpy(as_matrix(x))
            sparse = scipy.sparse.coo_matrix(dense)
            return sparse
        case _:
            return generic_conversion(x)




