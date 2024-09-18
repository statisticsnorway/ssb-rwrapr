import numpy as np
import rpy2
import rpy2.robjects.vectors as vc

from numpy.typing import NDArray

class RArray(np.ndarray):
    def __init__(self, Rdata):
        super().__init__(convert_numpy(Rdata))
        self.__Rattributes__ = None
    
    # def toR(self):
        # -> R-dataframe
        # -> R-Attributes -> convert to R
        # with_attributes: Callable = rcall("structure")
        # return with_attributes(R-dataframe, **R-Attributes) 

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
