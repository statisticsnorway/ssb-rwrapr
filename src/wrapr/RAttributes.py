from typing import Any
from typing import Callable
from typing import Dict

from .function_wrapper import rfunc


def get_Rattributes(x: Any) -> Dict:
    get_attr: Callable = rfunc("attributes")
    attributes = get_attr(x)
    return clean_basic_attributes(attributes)


def clean_basic_attributes(x: Dict) -> Dict:
    return {key: value for (key, value) in x if not exclude_condition(key)}


def exclude_condition(key: str) -> bool:
    return key in ["names", "class", "row.names"]
