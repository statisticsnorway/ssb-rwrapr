import rpy2.robjects as ro
import scipy

from typing import Any, Callable
from .rutils import rcall


class RObject():

    def __init__(self, Robj: Any):
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

    def to_py(self):
        from .convert_r2py import convert_r2py
        return convert_r2py(self.Robj)

    def toR(self):
        return self.Robj


def convert_s4(x: ro.methods.RS4) -> Any:
    from .rutils import get_rclass, as_matrix
    from .nputils import np_collapse
    from .RArray import convert_numpy

    rclass = get_rclass(x)
    if rclass is None:
        return RObject(x)

    match np_collapse(rclass):
        case "dgCMatrix": # to do: put this in a seperate function
            dense = convert_numpy(as_matrix(x))
            sparse = scipy.sparse.coo_matrix(dense)
            return sparse
        case _:
            return RObject(x)
