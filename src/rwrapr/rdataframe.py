import warnings
from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import pandas2ri

from .rattributes import get_Rattributes


class RDataFrame(pd.DataFrame):
    def __init__(self, data_frame: vc.DataFrame | pd.DataFrame):
        if isinstance(data_frame, vc.DataFrame):
            df = pandas2r(data_frame)
            attrs = get_attributes_dataframe(data_frame)
        else:
            df = data_frame
            attrs = None
        super().__init__(df) # type: ignore

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._Rattributes = attrs

    def toR(self) -> vc.DataFrame:
        from .rattributes import attributes2r
        from .rattributes import structure

        with (ro.default_converter + pandas2ri.converter).context():
            R_df = ro.conversion.get_conversion().py2rpy(self)

        if self._Rattributes is None:
            return R_df
        else:
            attributes = attributes2r(self._Rattributes)
            if attributes is None:
                return R_df
            return structure(R_df, **attributes)

    def toPy(self) -> pd.DataFrame:
        return pd.DataFrame(self)


def get_attributes_dataframe(df: vc.DataFrame) -> dict[str, Any] | None | Any:
    return get_Rattributes(df, exclude=["names", "class", "row.names"])


def pandas2r(df: vc.DataFrame) -> pd.DataFrame:
    with (ro.default_converter + pandas2ri.converter).context():
        pd_df: pd.DataFrame = ro.conversion.get_conversion().rpy2py(df)

    return pd_df


def attempt_pandas_conversion(data: Any) -> RDataFrame | TypeError:
    try:
        return RDataFrame(pd.DataFrame(data))
    except TypeError:
        return TypeError(f"This data will not convert {data}")
