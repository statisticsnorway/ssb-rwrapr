# Class which for function arguments which should not be evaluated eagerly
# in the python runtime environment, but instead lazily in the R runtime
# environment
from collections.abc import Callable
from typing import Any, Dict, List
from .rutils import rcall


class lazily():
    def __init__(self, expr: str) -> None:
        if not isinstance(expr, str):
            raise TypeError("lazy-expr must be in the form of a string")
        self.expr = expr

    def __str__(self) -> str:
        return self.expr


def lazy_wrap(args: List[Any], kwargs: Dict[str, Any],
              func: Callable, func_name: str | None) -> Callable | Any:
    lazy_arg_exprs: List[str] = []
    for x in args:
        if isinstance(x, lazily):
            raise TypeError(f"Lazy argument needs to be a keyword argument, {x} is unnamed")
    for k, v in kwargs.copy().items():
        if isinstance(v, lazily):
            lazy_arg_exprs.append(f"{k} = {str(v)}")
            del kwargs[k]

    if not lazy_arg_exprs:
        return func
    if func_name is None or func_name == "":
        raise ValueError("Lazy expressions not supported for unnamed functions")
    return rcall(f"function(...) {func_name}(..., {",".join(lazy_arg_exprs)})")


