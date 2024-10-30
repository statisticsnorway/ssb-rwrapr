from collections import OrderedDict
from collections import UserDict
from collections import UserList
from collections.abc import Callable
from typing import Any

import numpy as np
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc

from .rutils import rcall
from .toggle_rview import ToggleRView


class RList(UserList[Any]):
    def __init__(self, x: Any, attributes: dict[str, Any] | None):
        super().__init__(x)
        self._rattributes = attributes

    def to_r(self) -> Any:
        from .rattributes import attributes2r
        from .rattributes import structure

        # -> R-dataframe
        r_object = pylist2rlist(self)
        # -> R-Attributes -> convert to R
        if self._rattributes is None:
            return r_object
        r_attributes: dict[str, Any] | None = attributes2r(self._rattributes)

        if r_attributes:
            return structure(r_object, **r_attributes)
        return r_object

    def to_py(self) -> list[Any]:
        with ToggleRView(False):
            out = list(self)
        return out


ListTypes = list[Any] | tuple[Any] | set[Any] | RList


class RDict(UserDict[str, Any]):
    def __init__(self, x: Any, attributes: dict[str, Any] | None):
        super().__init__(x)
        self._rattributes = attributes

    def to_r(self) -> Any:
        from .rattributes import attributes2r
        from .rattributes import structure

        # -> R-dataframe
        r_object = dict2rlist(self)
        # -> R-Attributes -> convert to R
        if self._rattributes is None:
            return r_object
        r_attributes: dict[str, Any] | None = attributes2r(self._rattributes)

        if r_attributes:
            return structure(r_object, **r_attributes)
        return r_object

    def to_py(self) -> dict[str, Any]:
        with ToggleRView(False):
            out = dict(self)
        return out


DictTypes = dict[str, Any] | OrderedDict[str, Any] | UserDict[str, Any] | RDict


def convert_r2pylist(x_collection: ListTypes) -> list[Any] | tuple[Any]:
    from .convert_r2py import convert_r2py

    out: tuple[Any] | list[Any] = [convert_r2py(x) for x in x_collection]
    if isinstance(x_collection, tuple):
        out = tuple(out)
    return out


def convert_rlist2py(x_collection: vc.ListVector | vc.ListSexpVector) -> Any:
    from .rarray import convert_numpy
    from .rattributes import get_rattributes

    names = convert_numpy(x_collection.names, flatten=False)

    if isinstance(names, int | str | float | bool):
        names = np.array([names], dtype="U")

    if names is not None:
        fill = np.arange(1, len(names) + 1).astype("U")
        if names.itemsize < fill.itemsize:
            names = names.astype(fill.dtype)
        names[names == ""] = fill[names == ""]

    attributes = get_rattributes(x_collection, exclude=["names"])

    if attributes is not None:
        attributes = dict(attributes)

    if names is not None and len(names) and not np.any(names == ""):
        y = convert_r2pydict({n: x for n, x in zip(names, x_collection, strict=False)})
        return RDict(y, attributes=attributes)
    else:
        y = convert_r2pylist([x for x in x_collection])
        return RList(y, attributes=attributes)


def is_rlist(x_collection: Any) -> bool:
    match x_collection:
        case vc.ListVector() | vc.ListSexpVector():
            return True
        case _:
            return False


def convert_r2pydict(x_collection: DictTypes, is_rdict: bool = False) -> Any:
    from .convert_r2py import convert_r2py

    # this needs to be improved considering named vectors
    if is_rdict and np.all(np.array(x_collection.keys()) is None):
        y = list(zip(*x_collection.items(), strict=False))[1]
        x_collection = convert_r2py(y)
    elif is_rdict:
        x_collection = dict(x_collection)

    for key in x_collection:
        x_collection[key] = convert_r2py(x_collection[key])
    return x_collection


def dict2rlist(x: DictTypes) -> ro.ListVector:
    from .convert_py2r import convert_py2r

    return ro.ListVector({k: convert_py2r(v) for k, v in x.items()})


def pylist2rlist(x: ListTypes) -> ro.ListVector:
    y: dict[str, Any] = {str(k): v for k, v in enumerate(x)}
    unname: Callable[..., Any] = rcall("unname")
    return unname(dict2rlist(y))
