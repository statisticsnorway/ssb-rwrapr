import wrapr as wr
import pytest


pytest.fixture(scope="module")
def setup_wr():
    bs = wr.library("base", interactive=False)
    dt = wr.library("datasets", interactive=False)

    if bs is None or dt is None:
        pytest.fail(f"Setup failed with exception: {e}") 

    yield bs, dt


def test_setting_rview(setup_wr):
    bs, dt = setup_wr
    wr.settings.set_Rview(True)

    l2 = bs.list([1, 2, 3, 4])
    assert l2.toPy() == [1, 2, 3, 4]

    iris2 = dt.iris
    df = iris2.toPy()
    assert df.columns[0] == "Sepal.Length"
