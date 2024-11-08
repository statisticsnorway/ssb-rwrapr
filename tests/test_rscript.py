# type: ignore
import pytest

import rwrapr as wr


@pytest.fixture(scope="module")
def setup_wr():
    bs = wr.library("base", interactive=False)

    if bs is None:
        pytest.fail("Setup failed with exception: rpkg.PackageNotInstalledError")

    yield bs


def test_rscript_code(setup_wr):
    bs = setup_wr
    code = """
    l2 <- list(1, 2, 3, 4)
    iris2 <- iris
    library(dplyr)
    iris3 <- iris |> filter(Sepal.Length > 5) |>
        mutate(Sepal.Length = Sepal.Length * 14)
    """
    output = bs.rscript(code=code, extract=["l2", "iris2", "iris3"])
    assert isinstance(output, wr.RDict)
    assert output["l2"] == [1, 2, 3, 4]
    assert output["iris2"].columns[0] == "Sepal.Length"
    assert output["iris3"].columns[0] == "Sepal.Length"
    assert isinstance(output["iris3"], wr.RDataFrame)
    assert isinstance(output["iris2"], wr.RDataFrame)
    assert isinstance(output["l2"], wr.RList)


def test_rscript_path(setup_wr):
    bs = setup_wr

    path = "tests/rscript.R"
    output = bs.rscript(path=path, extract=["l2", "iris2", "iris3"])

    assert isinstance(output, wr.RDict)
    assert output["l2"] == [1, 2, 3, 4]
    assert output["iris2"].columns[0] == "Sepal.Length"
    assert output["iris3"].columns[0] == "Sepal.Length"
    assert isinstance(output["iris3"], wr.RDataFrame)
    assert isinstance(output["iris2"], wr.RDataFrame)
    assert isinstance(output["l2"], wr.RList)
