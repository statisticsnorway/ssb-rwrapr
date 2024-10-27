from collections.abc import Callable
from typing import Any

from .convert_py2r import convert_py_args2r
from .rlist import RDict


def get_rattributes(x: Any, exclude: list[str] | None = None) -> Any:
    from .function_wrapper import rfunc

    if exclude is None:
        exclude = []

    attributes: Callable[..., Any] = rfunc(
        """
    function(x, exclude) {
        attributes <- attributes(x)
        if (is.null(attributes)) return(NULL)

        attributes <- attributes[!names(attributes) %in% exclude]
        if (length(attributes) == 0) return(NULL)

        attributes
    }
    """
    )
    return attributes(x, exclude)


def structure(x: Any, **kwargs: Any) -> Any:
    from .rutils import rcall

    return rcall("structure")(x, **kwargs)


def attributes2r(attrs: dict[str, Any] | None | RDict) -> dict[str, Any]:
    if attrs is None:
        return {}
    modified_attrs = dict(attrs).copy()
    convert_py_args2r(args=[], kwargs=modified_attrs)
    return modified_attrs
