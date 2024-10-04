import numpy as np
import pytest

import ssb_wrapr as wr


dplyr = wr.library("dplyr")
dt = wr.library("datasets")


def test_last():
    assert dplyr.last(x=np.array([1, 2, 3, 4])) == 4
    assert dplyr.last(x=[1, 2, 3, 4]) == 4  # should now throw error


def test_mutate():
    iris = dt.iris
    df = dplyr.mutate(iris, Sepal=wr.lazily("round(Sepal.Length * 2, 0)"))

    assert np.all(np.round(df["Sepal.Length"] * 2) == df["Sepal"])
    with pytest.raises(TypeError):
        dplyr.mutate(iris, wr.lazily("Sepal.Length * 2"))
