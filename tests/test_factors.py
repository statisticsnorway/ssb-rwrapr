# type: ignore
import numpy as np

import rwrapr as wr


def test_factors():
    r = wr.library("base")
    x = r.factor(r.c("a", "b", "c", "b"))
    attrs = r.attributes(x)
    assert x._rattributes is None
    assert np.all(attrs["levels"] == ["a", "b", "c"])
    assert attrs["class"] == "factor"
