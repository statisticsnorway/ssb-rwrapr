from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import pandas2ri

from .rattributes import get_Rattributes


class RFactor(pd.Series):
    def __init__(self, r_factor: ro.vectors.FactorVector):
        super().__init__(convert_r_to_py(r_factor))
        self._Rattributes = get_attributes_factor(r_factor)

    def toR(self):
        return convert_to_r(self)

    def toPy(self):
        return pd.Series(self)


def get_attributes_factor(df: vc.FactorVector) -> dict[str, Any] | None:
    return get_Rattributes(df, exclude=["class", "levels"])


def convert_to_r(series: pd.Series):
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().py2rpy(series)

    return series


def convert_r_to_py(r_factor: ro.vectors.FactorVector):
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().rpy2py(r_factor)

    return pd.Series(series)
