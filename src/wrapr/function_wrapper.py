import rpy2.robjects as ro
import numpy as np

from numpy.typing import NDArray
from typing import Any, Callable, Dict, List
from .convert_py2r import convert_py_args2r
from .convert_r2py import convert_r2py
from .rutils import rcall
from .lazy_rexpr import lazy_wrap
from .settings import Settings, settings

def wrap_rfunc(func: Callable | Any, name: str | None) -> Callable | Any:
    from .RObject import RObject
    # should be a Callable, but may f-up (thus Any)
    if not callable(func):
        return None

    def wrap(*args, **kwargs):
        args = list(args) if args is not None else args # make args mutable
        # strip_args(args=args, kwargs=kwargs)
        convert_py_args2r(args=args, kwargs=kwargs)
        lazyfunc = lazy_wrap(args=args, kwargs=kwargs, func=func,
                             func_name=name)
        r_object: Any = lazyfunc(*args, **kwargs)
        if settings.Rview:
            return RObject(r_object)  
        else:
            return convert_r2py(r_object)


    try:
        wrap.__doc__ = func.__doc__
    except ro.HelpNotFoundError:
        pass
    return wrap


def rfunc(name: str) -> Callable | Any:
    # Function for getting r-function from global environment
    # BEWARE: THIS FUNCTION WILL TRY TO CONVERT ARGS GOING BOTH IN AND OUT!
    # This function must not be used in Rpy-in functions
    return wrap_rfunc(rcall(name), name=name)

