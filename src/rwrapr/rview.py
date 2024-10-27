from collections.abc import Callable
from collections.abc import Iterator
from typing import Any

import rpy2.robjects as ro
import scipy  # type: ignore

from .nputils import np_collapse
from .rlist import RDict
from .rlist import RList
from .rutils import as_matrix
from .rutils import get_rclass
from .toggle_rview import ToggleRView


class RView:
    def __init__(self, robj: Any):
        from .rarray import RArray
        from .rdataframe import RDataFrame

        if isinstance(robj, RArray | RDataFrame | RList | RDict):
            self.robj = robj.to_r()
        else:
            self.robj = robj

    def __str__(self) -> str | Any:
        # return captureRprint(self.Robj)
        return self.robj.__str__()

    def __repr__(self) -> str | Any:
        # return self.Robj.__repr__()
        return self.robj.__str__()

    def __getattr__(self, name: str) -> Any:
        from .function_wrapper import rfunc

        fun: Callable[..., Any] = rfunc(name)
        return fun(self.robj)

    def __getitem__(self, *args: Any) -> Any:
        return self.robj.__getitem__(*args)

    def __iter__(self) -> Iterator[Any] | Any:
        return self.robj.__iter__()

    def to_py(self, ignore_s3: bool = False) -> Any:
        from .convert_r2py import convert_r2py

        with ToggleRView(False):
            out = convert_r2py(self.robj, ignore_s3=ignore_s3)
        return out

    def to_r(self) -> Any:
        return self.robj


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
