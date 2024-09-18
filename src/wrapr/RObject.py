from typing import Any
from .rutils import rcall

class RObject():
    from .convert_r2py import convert_r2py
    from .function_wrapper import rfunc

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

    def toR(self):
        return self.Robj


