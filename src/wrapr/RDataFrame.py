from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import pandas2ri

from wrapr.RAttributes import get_Rattributes


class RDataFrame(pd.DataFrame):
    def __init__(self, data_frame: vc.DataFrame | pd.DataFrame):
        if isinstance(data_frame, vc.DataFrame):
            df = toPandas(data_frame)
            self.attrs["__Rattributes__"] = get_attributes_dataframe(data_frame)
        else:
            df = data_frame
        super().__init__(df)


def get_attributes_dataframe(df: vc.DataFrame) -> dict[str, Any] | None:
    return get_Rattributes(df, exclude=["names", "class", "row.names"])


def toR(df: RDataFrame) -> vc.DataFrame:
    with (ro.default_converter + pandas2ri.converter).context():
        R_df = ro.conversion.get_conversion().py2rpy(df)
    from .RAttributes import attributes2r
    from .RAttributes import structure

    attributes = attributes2r(df.attrs["__Rattributes__"])
    return structure(R_df, **attributes)


def toPandas(df: vc.DataFrame) -> pd.DataFrame:
    with (ro.default_converter + pandas2ri.converter).context():
        pd_df = ro.conversion.get_conversion().rpy2py(df)

    return pd_df


def attempt_pandas_conversion(data: Any) -> RDataFrame | TypeError:
    try:
        return RDataFrame(pd.DataFrame(data))
    except TypeError:
        return TypeError(f"This data will not convert {data}")
