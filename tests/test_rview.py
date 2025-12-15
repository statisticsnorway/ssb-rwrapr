# type: ignore
import pytest

import rwrapr as wr


@pytest.fixture(scope="module")
def setup_wr():
    bs = wr.library("base", interactive=False)
    dt = wr.library("datasets", interactive=False)
    md = wr.library("modsem", interactive=False)

    if bs is None or dt is None or md is None:
        pytest.fail("Setup failed with exception: rpkg.PackageNotInstalledError")

    yield bs, dt, md


def test_setting_rview(setup_wr):
    bs, dt, _md = setup_wr
    with wr.ToggleRView(True):
        l2 = bs.list(1, 2, 3, 4)
        assert isinstance(l2, wr.RView)
        assert l2.to_py() == [1, 2, 3, 4]

        iris2 = dt.iris
        df = iris2.to_py()
        assert isinstance(iris2, wr.RView)
        assert isinstance(df, wr.RDataFrame)
        assert df.columns[0] == "Sepal.Length"


def test_ignore_s3_warning(setup_wr):
    _bs, _dt, md = setup_wr

    m1 = """
      # Outer Model
      X =~ x1 + x2 +x3
      Y =~ y1 + y2 + y3
      Z =~ z1 + z2 + z3

      # Inner model
      Y ~ X + Z + X:Z
    """

    est = md.modsem(m1, data=md.oneInt, method="qml")

    with pytest.warns(UserWarning):
        est.to_py(ignore_s3_s4=False)
