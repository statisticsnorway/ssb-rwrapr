import wrapr as wr
import pandas as pd
import numpy as np
import pytest

@pytest.fixture(scope="module")
def dplyr():
    return wr.library("dplyr", interactive=False)

@pytest.fixture(scope="module")
def dt():
    return wr.library("datasets", interactive=False)

def test_last(dplyr):
    assert dplyr.last(x=np.array([1, 2, 3, 4])) == 4
    assert dplyr.last(x=[1, 2, 3, 4]) == 4 # should now throw error


def test_mutate(dplyr, dt):
    iris = dt.iris
    df = dplyr.mutate(iris, Sepal = wr.lazily("round(Sepal.Length * 2, 0)"))

    assert np.all(np.round(df["Sepal.Length"] * 2) == df["Sepal"])
    with pytest.raises(TypeError):
        dplyr.mutate(iris, wr.lazily("Sepal.Length * 2"))
