# type: ignore
import numpy as np
import pytest

import rwrapr as wr


@pytest.fixture(scope="module")
def setup_wr():
    try:
        R = wr.library("base")
        dt = wr.library("datasets")
        yield R, dt
    except Exception as e:
        pytest.fail(f"Setup failed with exception: {e}")


def test_pass_basefunc(setup_wr):
    R, dt = setup_wr

    iris = dt.iris
    R.apply(iris, MARGIN=1, FUN=R.paste, collapse=",")


def test_pass_customfuncs(setup_wr):
    R, _dt = setup_wr

    custom_func_scalar = R.function("""
    function(x) {
        # a scalar function so we can call Vectorize later
        sum(rep(x, max(floor(x), 1)))
    }
    """)

    assert custom_func_scalar(9) == 81

    custom_func_vector = R.Vectorize(custom_func_scalar)

    x = np.array([1, 2, 3, 4])

    assert (x**2 == custom_func_vector(x)).all()
