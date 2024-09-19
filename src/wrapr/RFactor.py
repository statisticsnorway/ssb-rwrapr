import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri


class RFactor(pd.Series):
    def __init__(self, r_factor: ro.vectors.FactorVector):
        super().__init__(convert_r_to_py(r_factor))

    def toR(self):
        return convert_to_r(self)

    def toPy(self):
        return pd.Series(self)


def convert_to_r(series: pd.Series):
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().py2rpy(series)

    return series


def convert_r_to_py(r_factor: ro.vectors.FactorVector):
    with (ro.default_converter + pandas2ri.converter).context():
        series = ro.conversion.get_conversion().rpy2py(r_factor)

    return pd.Series(series)
