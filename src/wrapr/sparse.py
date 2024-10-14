from collections.abc import Callable
from typing import Any

import rpy2.robjects as ro
import scipy


def convert_pysparsematrix(x: scipy.sparse.coo_array | scipy.sparse.coo_matrix) -> Any:
    from .rutils import rcall

    try:
        sparseMatrix: Callable = rcall("Matrix::sparseMatrix")
        return sparseMatrix(
            i=ro.IntVector(x.row + 1),
            j=ro.IntVector(x.col + 1),
            x=ro.FloatVector(x.data),
            dims=ro.IntVector(x.shape),
        )
    except Exception:
        return x
