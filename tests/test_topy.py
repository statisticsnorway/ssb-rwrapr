# type: ignore
import numpy as np
import pandas as pd

import rwrapr as wr


def test_to_py():
    bs = wr.library("base")
    rdict = bs.list(a=1, b=2, c=3, d=4)
    assert type(rdict) is wr.RDict
    assert type(rdict.to_py()) is dict

    rlist = bs.list(1, 2, 3, 4)
    assert type(rlist) is wr.RList
    assert type(rlist.to_py()) is list

    rarray = bs.c(1, 2, 3, 4)
    assert type(rarray) is wr.RArray
    assert type(rarray.to_py()) is np.ndarray

    rdataframe = bs.data_frame(a=np.array([1, 2, 3]), b=np.array([4, 5, 6]))
    assert type(rdataframe) is wr.RDataFrame
    assert type(rdataframe.to_py()) is pd.DataFrame
