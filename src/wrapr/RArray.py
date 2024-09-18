from typing import Any, Dict
import numpy as np
import rpy2
import rpy2.robjects.vectors as vc

from numpy.typing import NDArray

from wrapr.RAttributes import get_Rattributes
from wrapr.convert_py2r import convert_py2r


class RArray(np.ndarray):
    def __new__(cls, Rdata):
        from .RAttributes import get_Rattributes
        arr = convert_numpy(Rdata)
        obj = np.asarray(arr).view(cls)
        obj.__Rattributes__ = get_Rattributes(Rdata)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.__Rattributes__ = getattr(obj, '__Rattributes__', None)
    
    def toR(self):
        from .convert_py2r import convert_numpy2r
        from .RAttributes import structure, attributes2r
        # -> R-dataframe
        R_object = convert_numpy2r(self)
        # -> R-Attributes -> convert to R
        if self.__Rattributes__ is None:
            return R_object
        R_attributes = attributes2r(self.__Rattributes__)
        return structure(R_object, **R_attributes)
        
        # with_attributes: Callable = rcall("structure")
        # return with_attributes(R-dataframe, **R-Attributes) 


def get_RArray(x: Any) -> RArray | int:
    y: RArray = RArray(x)
    return y[0] if y.shape == (1,) and y.__Rattributes__ is None else y



def get_attributes_array(x) -> Dict | None:
    return get_Rattributes(x, exclude=["class", "dimnames", "dim"])


def convert_numpy(x: vc.Vector | NDArray, flatten: bool = False) -> NDArray | None:
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
    return filter_numpy(y, flatten=flatten)


def filter_numpy(x: NDArray, flatten: bool) -> NDArray | int | str | float | bool:
    # sometimes a numpy array will have one element with shape (,)
    # this should be (1,)
    y = x[np.newaxis][0] if not x.shape else x
    # if shape is (1,) we should just return as int | str | float | bool
    # R doesn't have these types, only vectors/arrays, this will probably
    # give unexpected results for users who are unfamiliar with R, so
    # we return the first element instead
    y = y[0] if y.shape == (1,) and flatten else y
    return y


def is_valid_numpy(x: NDArray) -> bool:
    return x.dtype.fields is None
