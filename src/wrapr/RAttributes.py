import numpy as np
from typing import Any
from typing import Callable
from typing import Dict

from .convert_py2r import convert_py_args2r

def get_attr(x, exclude) -> Any:
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


def get_Rattributes(x: Any, exclude: list = []) -> Dict | None:
    return get_attr(x, exclude = np.array(exclude))


def structure(x, **kwargs) -> Any:
    from .rutils import rcall
    return rcall("structure")(x, **kwargs)


def attributes2r(attrs: Dict[str, Any]) -> Dict[str, Any]:
    convert_py_args2r(args=[], kwargs=attrs)
    return attrs
