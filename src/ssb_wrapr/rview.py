from collections.abc import Callable
from typing import Any

import rpy2.robjects as ro
import scipy

from .nputils import np_collapse
from .rlist import RDict
from .rlist import RList
from .rutils import as_matrix
from .rutils import get_rclass


class RView:
    def __init__(self, Robj: Any):
        from .rarray import RArray
        from .rdataframe import RDataFrame

        if isinstance(Robj, RArray | RDataFrame | RList | RDict):
            self.Robj = Robj.toR()
        else:
            self.Robj = Robj

    def __str__(self) -> str:
        # return captureRprint(self.Robj)
        return self.Robj.__str__()

    def __repr__(self):
        # return self.Robj.__repr__()
        return self.Robj.__str__()

    def __getattr__(self, name: str) -> Any:
        from .function_wrapper import rfunc

        fun: Callable = rfunc(name)
        return fun(self.Robj)

    def __getitem__(self, *args):
        return self.Robj.__getitem__(*args)

    def __iter__(self):
        return self.Robj.__iter__()

    def toPy(self, ignoreS3=False):
        from .convert_r2py import convert_r2py

        return convert_r2py(self.Robj, ignoreS3=ignoreS3)

    def toR(self):
        return self.Robj


def convert_s4(x: ro.methods.RS4) -> Any:
    from .rarray import convert_numpy

    rclass = get_rclass(x)
    if rclass is None:
        return RView(x)

    match np_collapse(rclass):
        case "dgCMatrix":  # todo: put this in a separate function
            dense = convert_numpy(as_matrix(x))
            sparse = scipy.sparse.coo_matrix(dense)
            return sparse
        case _:
            return RView(x)
