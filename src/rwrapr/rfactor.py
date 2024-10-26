from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import pandas2ri

from .rattributes import get_rattributes
from .toggle_rview import ToggleRView


class RFactor(pd.Series):  # type: ignore
    def __init__(self, r_factor: ro.vectors.FactorVector):
        super().__init__(convert_rfactor2py(r_factor))  # type: ignore
        self._rattributes = get_attributes_factor(r_factor)

    def to_r(self) -> ro.vectors.FactorVector | Any:
        return convert_categorical2r(self)

    def to_py(self) -> pd.Series:  # type: ignore
        with ToggleRView(False):
            out = pd.Series(self)
        return out


def get_attributes_factor(df: vc.FactorVector) -> dict[str, Any] | None | Any:
    return get_rattributes(df, exclude=["class", "levels"])


def convert_categorical2r(series: pd.Series) -> ro.vectors.FactorVector | Any:  # type: ignore
    with (ro.default_converter + pandas2ri.converter).context():
        r_factor = ro.conversion.get_conversion().py2rpy(series)

    return r_factor


def convert_rfactor2py(r_factor: ro.vectors.FactorVector) -> pd.Series:  # type: ignore
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().rpy2py(r_factor)
    return pd.Series(series)  # type: ignore
