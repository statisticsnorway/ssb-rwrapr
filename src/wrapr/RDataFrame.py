import pandas as pd

import rpy2.robjects as ro
import rpy2.robjects.vectors as vc

from typing import Any
from .RArray import convert_numpy

def convert_pandas(df: vc.DataFrame) -> pd.DataFrame:
    colnames = df.names
    df_dict = {c: convert_numpy(x) for c, x in zip(colnames, list(df))}
    return pd.DataFrame(df_dict) 


def attempt_pandas_conversion(x: Any) -> Any:
    try: 
        return pd.DataFrame(x)
    except:
        return x
