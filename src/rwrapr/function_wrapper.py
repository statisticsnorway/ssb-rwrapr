from collections.abc import Callable
from typing import Any
from typing import TypeAlias

import rpy2.robjects.help as rhelp

from .convert_py2r import convert_py_args2r
from .convert_r2py import convert_r2py
from .lazy_rexpr import lazy_wrap
from .rarray import RArray
from .rdataframe import RDataFrame
from .rfactor import RFactor
from .rlist import RDict
from .rlist import RList
from .rutils import rcall
from .rview import RView
from .settings import settings


RReturnType: TypeAlias = RView | RArray | RDataFrame | RFactor | RList | RDict | Any


def wrap_rfunc(
    func: Callable[..., Any], name: str | None
) -> Callable[..., RReturnType]:
    if not callable(func):
        raise ValueError(f"The provided `func` argument: {name} is not callable")

    def wrap(*args: Any, **kwargs: Any) -> RReturnType:
        # make args mutable
        args = list(args) if args is not None else args  # type: ignore[assignment]
        convert_py_args2r(args=args, kwargs=kwargs)  # type: ignore[arg-type]
        lazyfunc = lazy_wrap(args=args, kwargs=kwargs, func=func, func_name=name)  # type: ignore[arg-type]
        r_object: Any = lazyfunc(*args, **kwargs)
        if settings.Rview:
            return RView(r_object)
        else:
            return convert_r2py(r_object)

    try:
        wrap.__doc__ = func.__doc__
    except rhelp.HelpNotFoundError:
        pass
    return wrap


def rfunc(name: str) -> Callable[..., RReturnType]:
    # Function for getting r-function from global environment
    # BEWARE: THIS FUNCTION WILL TRY TO CONVERT ARGS GOING BOTH IN AND OUT!
    # This function must not be used in Rpy-in functions
    return wrap_rfunc(rcall(name), name=name)
