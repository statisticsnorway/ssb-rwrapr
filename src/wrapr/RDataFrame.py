from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc

from typing import Any

from wrapr.RAttributes import get_Rattributes
from wrapr.rutils import rcall

from .RArray import convert_numpy


class RDataFrame(pd.DataFrame):
    def __init__(self, Rdata):
        super().__init__(convert_pandas(Rdata))
        self.attrs["__Rattributes__"] = get_attributes_dataframe(Rdata)
    # def toR(self):
    # -> R-dataframe
    # -> R-Attributes -> convert to R
    # with_attributes: Callable = rcall("structure")
    # return with_attributes(R-dataframe, **R-Attributes)



def get_attributes_dataframe(df) -> dict[str, Any] | None:
    # Rlist[...] -> f() -> Dict[WrappedObjects]
    return get_Rattributes(df, exclude=["names", "class", "row.names"])


def convert_pandas(df: vc.DataFrame) -> pd.DataFrame:
    from rpy2.robjects import pandas2ri

    with (ro.default_converter + pandas2ri.converter).context():
        pd_df = ro.conversion.get_conversion().rpy2py(df)

    return pd_df
