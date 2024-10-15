import numpy as np
import pytest

import rwrapr as wr


@pytest.fixture(scope="module")
def setup_wr():
    try:
        dplyr = wr.library("dplyr")
        dt = wr.library("datasets")
        yield dplyr, dt
    except Exception as e:
        pytest.fail(f"Setup failed with exception: {e}")


def test_last(setup_wr):
    dplyr, dt = setup_wr

    assert dplyr.last(x=np.array([1, 2, 3, 4])) == 4
    assert dplyr.last(x=[1, 2, 3, 4]) == 4  # should now throw error


def test_mutate(setup_wr):
    dplyr, dt = setup_wr
    iris = dt.iris
    df = dplyr.mutate(iris, Sepal=wr.lazily("round(Sepal.Length * 2, 0)"))

    assert np.all(np.round(df["Sepal.Length"] * 2) == df["Sepal"])
    with pytest.raises(TypeError):
        dplyr.mutate(iris, wr.lazily("Sepal.Length * 2"))
