# type: ignore
import pytest
import rwrapr as wr


@pytest.fixture(scope="module")
def setup_wr():
    bs = wr.library("base", interactive=False)
    dt = wr.library("datasets", interactive=False)

    if bs is None or dt is None:
        pytest.fail("Setup failed with exception: rpkg.PackageNotInstalledError")

    yield bs, dt


def test_setting_rview(setup_wr):
    bs, dt = setup_wr
    with wr.ToggleRView(True):
        l2 = bs.list(1, 2, 3, 4)
        assert isinstance(l2, wr.RView)
        assert l2.toPy() == [1, 2, 3, 4]

        iris2 = dt.iris
        df = iris2.toPy()
        assert isinstance(iris2, wr.RView)
        assert isinstance(df, wr.RDataFrame)
        assert df.columns[0] == "Sepal.Length"
