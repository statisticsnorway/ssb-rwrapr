# type: ignore
import numpy as np

import rwrapr as wr


def test_subsetting_rarray():
    bs = wr.library("base")
    arr = bs.c(a=1, b=2, c=3, d=4)
    arr.to_r()
    arr[0:2].to_r()
    arr[arr > 2].to_r()
    assert np.all(arr[0:2]._rattributes["names"] == ["a", "b"])

    arr = bs.matrix(
        np.arange(12) + 1,
        nrow=4,
        ncol=3,
        dimnames=bs.list(bs.c("a", "b", "c", "d"), bs.c("A", "B", "C")),
    )
    arr.to_r()
    arr[0:2, 0:2].to_r()
    arr[np.sum(arr, axis=1) > 20, :].to_r()
    assert np.all(arr[0:2, 0:2]._rattributes["dimnames"][0] == ["a", "b"])
    assert np.all(arr[0:2, 0:2]._rattributes["dimnames"][1] == ["A", "B"])
    assert np.all(
        arr[np.sum(arr, axis=1) > 20, :]._rattributes["dimnames"][0] == ["c", "d"]
    )
    assert np.all(
        arr[np.sum(arr, axis=1) > 20, :]._rattributes["dimnames"][1] == ["A", "B", "C"]
    )
