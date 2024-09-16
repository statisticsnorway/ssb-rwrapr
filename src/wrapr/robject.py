from logging import captureWarnings
from typing import Any
import rpy2.robjects as ro
from .rutils import rcall
from .convert_r2py import convert_r2py


class Robject():
    def __init__(self, Robj: Any):
        self.Robj = Robj

    def __str__(self) -> str:
        return captureRprint(self.Robj) 

    def __repr__(self):
        return self.Robj.__repr__()

    def __getattr__(self, name: str) -> Any:
        fun: Callable = rfunc(name)
        return fun(self.Robj)

    def __getitem__(self, *args):
        return self.Robj.__getitem__(*args)

    def __iter__(self):
        return self.Robj.__iter__()

    
def captureRprint(x) -> str:
    expr = r'function(x) paste(utils::capture.output(print(x)), collapse = "\n")'
    return convert_r2py(rcall(expr)(x)[0])
