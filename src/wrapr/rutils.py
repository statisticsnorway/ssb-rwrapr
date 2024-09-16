import rpy2.robjects as ro
from typing import Any


def rcall(expr: str) -> Any:
    return ro.r(expr, print_r_warnings=False, invisible=True)
