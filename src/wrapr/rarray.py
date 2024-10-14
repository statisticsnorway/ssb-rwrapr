import warnings
from collections.abc import Callable
from typing import Any

import numpy as np
import rpy2
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from numpy.typing import NDArray

from .convert_py2r import convert_py2r
from .rattributes import get_Rattributes


class RArray(np.ndarray):
    def __new__(cls, Rdata):

        arr = convert_numpy(Rdata)
        if not isinstance(arr, np.ndarray):
            raise TypeError("convert_numpy(Rdata) must return a numpy.ndarray")

        # Ensure the array is in C order
        arr_c = np.ascontiguousarray(arr)
        obj = arr_c.view(cls)

        obj._Rattributes = get_attributes_array(Rdata)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        # Copy the _Rattributes from the source object
        self._Rattributes = getattr(obj, "_Rattributes", None)

    def __getitem__(self, index):
        result = super().__getitem__(index)

        # If the result is not an instance of RArray, return it as is
        if not isinstance(result, RArray):
            return result

        # Copy the _Rattributes
        if hasattr(self, "_Rattributes") and self._Rattributes is not None:
            result._Rattributes = getattr(self, "_Rattributes", {}).copy()

            orig_dimnames = self._Rattributes.get("dimnames", None)
            orig_names = self._Rattributes.get("names", None)
            orig_dim = self._Rattributes.get("dim", None)

            ndim_self = self.ndim
            ndim_result = result.ndim

            # Normalize the index to match the number of dimensions
            index_normalized = self._normalize_index(index, ndim_self)

            # Determine which dimensions are kept after indexing
            dims_kept = self._get_dims_kept(index_normalized)

            # Update dimnames for multi-dimensional arrays
            if orig_dimnames is not None:
                new_dimnames = []
                for i, keep_dim in enumerate(dims_kept):
                    if i >= len(orig_dimnames):
                        continue  # No dimname for this dimension

                    names = orig_dimnames[i]
                    idx = index_normalized[i]

                    if keep_dim:
                        if names is None:
                            new_dimnames.append(None)
                        else:
                            names_array = np.array(names)
                            try:
                                new_names = names_array[idx]
                            except Exception:
                                indices = np.arange(len(names_array))[idx]
                                new_names = names_array[indices]

                            new_dimnames.append(new_names)
                    else:
                        # Dimension is removed, do not add dimname
                        pass

                result._Rattributes["dimnames"] = new_dimnames

            # Update names for 1D arrays
            elif orig_names is not None:
                if ndim_self == 1 and ndim_result >= 1:
                    names = orig_names
                    idx = index_normalized[0]
                    names_array = np.array(names)
                    try:
                        new_names = names_array[idx]
                    except Exception:
                        indices = np.arange(len(names_array))[idx]
                        new_names = names_array[indices]

                    result._Rattributes["names"] = new_names
                elif ndim_self == 1 and ndim_result == 0:
                    result._Rattributes.pop("names", None)

            if orig_dim is not None:
                if ndim_result > 0:
                    new_dim = result.shape
                    new_dim_array = np.array(new_dim)
                    result._Rattributes["dim"] = new_dim_array
                else:
                    # Result is scalar, remove 'dim' attribute
                    result._Rattributes.pop("dim", None)

        return result

    def _normalize_index(self, index, ndim):
        if not isinstance(index, tuple):
            index = (index,)

        index_list = []
        ellipsis_expanded = False

        for idx in index:
            if idx is Ellipsis:
                if ellipsis_expanded:
                    raise IndexError("Only one ellipsis allowed in index")
                num_missing = ndim - len(index) + 1
                index_list.extend([slice(None)] * num_missing)
                ellipsis_expanded = True
            else:
                index_list.append(idx)

        if len(index_list) < ndim:
            index_list.extend([slice(None)] * (ndim - len(index_list)))

        return tuple(index_list[:ndim])

    def _get_dims_kept(self, index_normalized):
        dims_kept = []
        for idx in index_normalized:
            if isinstance(idx, slice | type(None) | type(Ellipsis)):
                dims_kept.append(True)
            elif np.isscalar(idx):
                dims_kept.append(False)
            elif isinstance(idx, list | np.ndarray):
                dims_kept.append(True)
            else:
                # Unknown type, assume dimension is kept
                dims_kept.append(True)
        return dims_kept

    def toR(self):
        from .rattributes import attributes2r
        from .rattributes import structure

        R_object = convert_numpy2r(np.asarray(self))
        if self._Rattributes is not None:
            R_attributes = attributes2r(self._Rattributes)
            R_object = structure(R_object, **R_attributes)

        return R_object

    def toPy(self):
        return np.asarray(self)


def get_RArray(x: Any) -> RArray | NDArray:
    y: RArray = RArray(x)
    return y[0] if y.shape == (1,) and y._Rattributes is None else y


def get_attributes_array(x) -> dict | None:
    return get_Rattributes(x, exclude=["class"])


def convert_numpy(
    x: vc.Vector | NDArray, flatten: bool = False
) -> NDArray | int | str | float | bool | None:
    if isinstance(x, rpy2.rinterface_lib.sexp.NULLType):
        return None
    match x:  # this should be expanded upon
        case vc.BoolVector() | vc.BoolArray() | vc.BoolMatrix():
            dtype = "bool"
        case vc.FloatVector() | vc.FloatArray() | vc.FloatMatrix():
            dtype = "float"
        case vc.IntVector() | vc.IntArray() | vc.IntMatrix():
            dtype = "int"
        case vc.StrArray() | vc.StrVector() | vc.StrMatrix():
            dtype = "U"
        case _:
            dtype = None

    y = np.asarray(x, dtype=dtype)
    return filter_numpy(y, flatten=flatten)


def filter_numpy(x: NDArray, flatten: bool) -> NDArray | int | str | float | bool:
    # sometimes a numpy array will have one element with shape (,)
    # this should be (1,)
    y = x[np.newaxis][0] if not x.shape else x
    # if shape is (1,) we should just return as int | str | float | bool
    # R doesn't have these types, only vectors/arrays, this will probably
    # give unexpected results for users who are unfamiliar with R, so
    # we return the first element instead
    y = y[0] if y.shape == (1,) and flatten else y
    return y


def is_valid_numpy(x: NDArray) -> bool:
    return x.dtype.fields is None


def convert_numpy2r(x: NDArray) -> Any:  # RBaseObject:
    y = x.copy()
    if not y.shape:
        y = y[np.newaxis]
    match len(y.shape):
        case 0:
            raise ValueError("Unexpected shape of numpy array")
        case 1:
            return convert_numpy1D(y)
        case 2:
            return convert_numpy2D(y)
        case _:
            return convert_numpyND(y)


def convert_numpy1D(x: NDArray) -> Any:  # RBaseObject:
    match x.dtype.kind:
        case "b":
            return ro.BoolVector(x)
        case "i":
            return ro.IntVector(x)
        case "f":
            return ro.FloatVector(x)
        case "U" | "S":
            return ro.StrVector(x)
        case "O":
            try:
                y = x.astype("U")
            except Exception:
                warnings.warn(
                    "dtype = object is not supported, this will probably not work",
                    stacklevel=2,
                )
                y = convert_py2r(x.tolist())
            return ro.StrVector(y)
        case _:
            return x


def convert_numpy2D(x: NDArray) -> Any:  # RBaseObject:
    flat_x: NDArray = x.flatten(order="F")
    nrow, ncol = x.shape
    y = convert_numpy1D(flat_x)
    f: Callable = ro.r("matrix")
    return f(y, nrow=nrow, ncol=ncol)


def convert_numpyND(x: NDArray) -> Any:  # RBaseObject:
    flat_x: NDArray = x.flatten(order="F")
    dim: tuple = x.shape
    y = convert_numpy1D(flat_x)
    f: Callable = ro.r("array")
    return f(y, dim=ro.IntVector(dim))
