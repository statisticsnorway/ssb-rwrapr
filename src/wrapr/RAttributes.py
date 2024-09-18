from typing import Any
from typing import Callable
from typing import Dict

from .convert_py2r import convert_py_args2r


def get_Rattributes(x: Any, exclude: list = []) -> Dict | None:
    from .function_wrapper import rfunc
    get_attr: Callable = rfunc("attributes")
    attributes = get_attr(x)
    if attributes is None:
        return None
    return clean_basic_attributes(attributes, exclude=exclude)


def clean_basic_attributes(x: Dict, exclude: list = []) -> Dict:
    return {key: value for (key, value) in x.items() if not exclude_condition(key, exclude=exclude)}


def exclude_condition(key: str, exclude: list = []) -> bool:
    return key in exclude


def structure(x, **kwargs) -> Any:
    from .rutils import rcall
    return rcall("structure")(x, **kwargs)


def attributes2r(attrs: Dict[str, Any]) -> Dict[str, Any]:
    convert_py_args2r(args=[], kwargs=attrs)
    return attrs
