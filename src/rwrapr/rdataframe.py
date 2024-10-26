import warnings
from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import pandas2ri

from .rattributes import get_rattributes
from .toggle_rview import ToggleRView


class RDataFrame(pd.DataFrame):
    def __init__(self, data_frame: vc.DataFrame | pd.DataFrame):
        if isinstance(data_frame, vc.DataFrame):
            df = r2pandas(data_frame)
            attrs = get_attributes_dataframe(data_frame)
        else:
            df = data_frame
            attrs = None
        super().__init__(df)  # type: ignore

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._rattributes = attrs

    def to_r(self) -> vc.DataFrame:
        from .rattributes import attributes2r
        from .rattributes import structure

        r_df = pandas2r(self)
        if self._rattributes is None:
            return r_df
        else:
            attributes = attributes2r(self._rattributes)
            if not attributes:
                return r_df
            return structure(r_df, **attributes)

    def to_py(self) -> pd.DataFrame:
        with ToggleRView(False):
            out = pd.DataFrame(self)
        return out


def get_attributes_dataframe(df: vc.DataFrame) -> dict[str, Any] | None | Any:
    return get_rattributes(df, exclude=["names", "class", "row.names"])


def pandas2r(df: pd.DataFrame) -> vc.DataFrame:
    with (ro.default_converter + pandas2ri.converter).context():
        rdf: vc.DataFrame = ro.conversion.get_conversion().py2rpy(df)
    return rdf


def r2pandas(df: vc.DataFrame) -> pd.DataFrame:
    with (ro.default_converter + pandas2ri.converter).context():
        pdf: pd.DataFrame = ro.conversion.get_conversion().rpy2py(df)
    return pdf


def attempt_pandas_conversion(data: Any) -> RDataFrame | TypeError:
    try:
        return RDataFrame(pd.DataFrame(data))
    except TypeError:
        return TypeError(f"This data will not convert {data}")
