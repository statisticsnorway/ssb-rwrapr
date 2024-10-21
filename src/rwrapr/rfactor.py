import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc

from typing import Any
from rpy2.robjects import pandas2ri

from .rattributes import get_Rattributes
from .toggle_rview import ToggleRView


class RFactor(pd.Series): # type: ignore
    def __init__(self, r_factor: ro.vectors.FactorVector):
        super().__init__(convert_rfactor2py(r_factor)) # type: ignore
        self._Rattributes = get_attributes_factor(r_factor)

    def toR(self) -> ro.vectors.FactorVector | Any:
        return convert_categorical2r(self)

    def toPy(self) -> pd.Series: # type: ignore
        with ToggleRView(False):
            out = pd.Series(self)
        return out


def get_attributes_factor(df: vc.FactorVector) -> dict[str, Any] | None | Any:
    return get_Rattributes(df, exclude=["class", "levels"])


def convert_categorical2r(series: pd.Series) -> ro.vectors.FactorVector | Any: # type: ignore
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().py2rpy(series)

    return series


def convert_rfactor2py(r_factor: ro.vectors.FactorVector) -> pd.Series: # type: ignore
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().rpy2py(r_factor)
    return pd.Series(series) # type: ignore
