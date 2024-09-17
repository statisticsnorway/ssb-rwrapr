import pandas as pd

import rpy2.robjects as ro
import rpy2.robjects.vectors as vc

from typing import Any

from wrapr.rutils import rcall
from .RArray import convert_numpy


class RDataFrame(pd.DataFrame):
    def __init__(self, Rdata):
        super().__init__(convert_pandas(Rdata))
        self.attrs["__Rattributes__"] = get_attributes_dataframe()
    
    # def toR(self):
        # -> R-dataframe
        # -> R-Attributes -> convert to R
        # with_attributes: Callable = rcall("structure")
        # return with_attributes(R-dataframe, **R-Attributes) 


def get_attributes_dataframe():
    # Rlist[...] -> f() -> Dict[WrappedObjects]
    return {"some attribute": "hello there"}


def convert_pandas(df: vc.DataFrame) -> pd.DataFrame:
    colnames = df.names
    df_dict = {c: convert_numpy(x) for c, x in zip(colnames, list(df))}
    return pd.DataFrame(df_dict) 


def attempt_pandas_conversion(x: Any) -> Any:
    try: 
        return pd.DataFrame(x)
    except:
        return x
