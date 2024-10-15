from collections import OrderedDict
from collections import UserDict
from collections import UserList
from collections.abc import Callable
from typing import Any

import numpy as np
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc

from .rutils import rcall


class RList(UserList[Any]):
    def __init__(self, x: Any, attributes: dict[str, Any] | None):
        super().__init__(x)
        self._Rattributes = attributes

    def toR(self) -> Any:
        from .rattributes import attributes2r
        from .rattributes import structure

        # -> R-dataframe
        R_object = pylist2rlist(self)
        # -> R-Attributes -> convert to R
        if self._Rattributes is None:
            return R_object
        R_attributes: dict[str, Any] | None = attributes2r(self._Rattributes)

        if R_attributes:
            return structure(R_object, **R_attributes)
        return R_object

    def toPy(self) -> list[Any]:
        return list(self)


class RDict(UserDict[str, Any]):
    def __init__(self, x: Any, attributes: dict[str, Any] | None):
        super().__init__(x)
        self._Rattributes = attributes

    def toR(self) -> Any:
        from .rattributes import attributes2r
        from .rattributes import structure

        # -> R-dataframe
        R_object = dict2rlist(self)
        # -> R-Attributes -> convert to R
        if self._Rattributes is None:
            return R_object
        R_attributes: dict[str, Any] | None = attributes2r(self._Rattributes)

        if R_attributes:
            return structure(R_object, **R_attributes)
        return R_object

    def toPy(self) -> dict[str, Any]:
        return dict(self)


def convert_r2pylist(X: list[Any] | tuple[Any] | RList) -> list[Any] | tuple[Any]:
    from .convert_r2py import convert_r2py

    out: tuple[Any] | list[Any] = [convert_r2py(x) for x in X]
    if isinstance(X, tuple):
        out = tuple(out)
    return out


def convert_rlist2py(X: vc.ListVector | vc.ListSexpVector) -> Any:
    from .rarray import convert_numpy
    from .rattributes import get_Rattributes

    names = convert_numpy(X.names, flatten=False)
    if isinstance(names, int | str | float | bool):
        names = np.array([names], dtype="U")

    attributes = get_Rattributes(X, exclude=["names"])

    if names is not None and len(names) and not np.any(names == ""):
        y = convert_r2pydict({n: x for n, x in zip(names, X, strict=False)})
        return RDict(y, attributes=attributes)
    else:
        y = convert_r2pylist([x for x in X])
        return RList(y, attributes=attributes)


def is_rlist(X: Any) -> bool:
    match X:
        case vc.ListVector() | vc.ListSexpVector():
            return True
        case _:
            return False


def convert_r2pydict(
    X: dict[str, Any] | OrderedDict[str, Any] | UserDict[str, Any] | RDict,
    is_RDict: bool = False,
) -> Any:
    from .convert_r2py import convert_r2py

    # this needs to be improved considering named vectors
    if is_RDict and np.all(np.array(X.keys()) is None):
        Y = list(zip(*X.items(), strict=False))[1]
        X = convert_r2py(Y)
    elif is_RDict:
        X = dict(X)

    for key in X:
        X[key] = convert_r2py(X[key])
    return X


def dict2rlist(x: dict[str, Any] | OrderedDict[str, Any] | RDict) -> ro.ListVector:
    from .convert_py2r import convert_py2r

    return ro.ListVector({k: convert_py2r(v) for k, v in x.items()})


def pylist2rlist(x: list[Any] | tuple[Any] | set[Any] | RList) -> ro.ListVector:
    y: dict[str, Any] = {str(k): v for k, v in enumerate(x)}
    unname: Callable[..., Any] = rcall("unname")
    return unname(dict2rlist(y))
