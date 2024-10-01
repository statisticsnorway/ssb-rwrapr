import wrapr as wr
import pandas as pd
import numpy as np
import pytest

def test_factors():
    R = wr.library("base")
    x = R.factor(R.c("a", "b", "c", "b"))
    attrs = R.attributes(x)
    assert x._Rattributes is None
    assert np.all(attrs["levels"] == ["a", "b", "c"])
    assert attrs["class"] == "factor"
