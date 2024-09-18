from typing import Any
from typing import Callable
from typing import Dict

from .function_wrapper import rfunc


def get_Rattributes(x: Any, exclude: list = []) -> Dict:
    get_attr: Callable = rfunc("attributes")
    attributes = get_attr(x)
    return clean_basic_attributes(attributes, exclude=exclude)


def clean_basic_attributes(x: Dict, exclude: list = []) -> Dict:
    return {key: value for (key, value) in x.items() if not exclude_condition(key, exclude=exclude)}


def exclude_condition(key: str, exclude: list = []) -> bool:
    return key in exclude
