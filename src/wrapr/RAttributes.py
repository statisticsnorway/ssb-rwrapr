import numpy as np
from typing import Any
from typing import Callable
from typing import Dict

from .convert_py2r import convert_py_args2r

def get_Rattributes(x, exclude = []) -> Any:
    from .function_wrapper import rfunc
    attributes: Callable = rfunc("""
    function(x, exclude) {
        attributes <- attributes(x)
        if (is.null(attributes)) return(NULL)

        attributes <- attributes[!names(attributes) %in% exclude]
        if (length(attributes) == 0) return(NULL)

        attributes
    } 
    """)
    return attributes(x, exclude)


def structure(x, **kwargs) -> Any:
    from .rutils import rcall
    return rcall("structure")(x, **kwargs)


def attributes2r(attrs: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if attrs is None:
        return {}
    modified_attrs = attrs.copy()
    convert_py_args2r(args=[], kwargs=modified_attrs)
    return modified_attrs
