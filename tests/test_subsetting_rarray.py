# type: ignore
import numpy as np
import rwrapr as wr


def test_SubsettingRArray():
    bs = wr.library("base")
    arr = bs.c(a=1, b=2, c=3, d=4)
    arr.toR()
    arr[0:2].toR()
    arr[arr > 2].toR()
    assert np.all(arr[0:2]._Rattributes["names"] == ["a", "b"])

    arr = bs.matrix(
        np.arange(12) + 1,
        nrow=4,
        ncol=3,
        dimnames=bs.list(bs.c("a", "b", "c", "d"), bs.c("A", "B", "C")),
    )
    arr.toR()
    arr[0:2, 0:2].toR()
    arr[np.sum(arr, axis=1) > 20, :].toR()
    assert np.all(arr[0:2, 0:2]._Rattributes["dimnames"][0] == ["a", "b"])
    assert np.all(arr[0:2, 0:2]._Rattributes["dimnames"][1] == ["A", "B"])
    assert np.all(
        arr[np.sum(arr, axis=1) > 20, :]._Rattributes["dimnames"][0] == ["c", "d"]
    )
    assert np.all(
        arr[np.sum(arr, axis=1) > 20, :]._Rattributes["dimnames"][1] == ["A", "B", "C"]
    )
