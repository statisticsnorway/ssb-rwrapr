from collections.abc import Callable
from typing import Any

import rpy2.robjects as ro

from .convert_py2r import convert_py_args2r
from .convert_r2py import convert_r2py
from .lazy_rexpr import lazy_wrap
from .rutils import rcall
from .RView import RView
from .settings import settings


def wrap_rfunc(
    func: Callable[..., Any], name: str | None
) -> Callable[..., Any] | RView | Any | None:
    # TODO: Removed the Any-part of func type annotation. Check why Any was needed.
    # should be a Callable, but may f-up (thus Any)
    if not callable(func):
        return None  # TODO: Should throw exception instead? Why wrap something that is not callable?

    def wrap(*args, **kwargs):
        args = list(args) if args is not None else args  # make args mutable
        # strip_args(args=args, kwargs=kwargs)
        convert_py_args2r(args=args, kwargs=kwargs)
        lazyfunc = lazy_wrap(args=args, kwargs=kwargs, func=func, func_name=name)
        r_object: Any = lazyfunc(*args, **kwargs)
        if settings.Rview:
            return RView(r_object)
        else:
            return convert_r2py(r_object)

    try:
        wrap.__doc__ = func.__doc__
    except ro.HelpNotFoundError:
        pass
    return wrap


def rfunc(name: str) -> Callable[..., Any] | RView | Any | None:
    # Function for getting r-function from global environment
    # BEWARE: THIS FUNCTION WILL TRY TO CONVERT ARGS GOING BOTH IN AND OUT!
    # This function must not be used in Rpy-in functions
    return wrap_rfunc(rcall(name), name=name)
