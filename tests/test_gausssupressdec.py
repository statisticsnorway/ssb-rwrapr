# type: ignore
import numpy as np

import rwrapr as wr


base = wr.importr("base")
GaussSuppression = wr.importr("GaussSuppression")
SSBtools = wr.importr("SSBtools")


def test_gausssuppressdec_and_more():
    base.set_seed(123)
    z2 = SSBtools.SSBtoolsData("z2")
    z2["y1"] = base.runif(base.nrow(z2))
    z2["y2"] = base.runif(base.nrow(z2))
    print_inc = False

    # Error here if overlapping freqVar, numVar, weightVar not treated correctly.
    a = GaussSuppression.GaussSuppressDec(
        z2,
        formula="~region * fylke * kostragr * hovedint",
        freqVar="ant",
        protectZeros=False,
        maxN=2,
        numVar=np.array(["y1", "y2", "ant"]),
        weightVar="y1",
        printInc=print_inc,
    )
    GaussSuppression.GaussSuppressDec(
        z2,
        formula=wr.Lazily("~region * fylke * kostragr * hovedint"),  # this also works
        freqVar="ant",
        protectZeros=False,
        maxN=2,
        numVar=np.array(["y1", "y2", "ant"]),
        weightVar="y1",
        printInc=print_inc,
    )

    # Recalculate suppression from decimals. "kostragr" not included.
    b = GaussSuppression.SuppressionFromDecimals(
        a.loc[a["isInner"].astype("bool"), :],
        hierarchies=SSBtools.FindDimLists(z2[["region", "fylke", "hovedint"]]),
        freqVar="ant",
        decVar="freqDec",
        printInc=print_inc,
    )

    # Special case where all suppressions found in suppressedData.
    d = GaussSuppression.AdditionalSuppression(
        z2,
        suppressedData=a,
        dimVar=np.array(["region", "fylke", "hovedint"]),
        freqVar="ant",
        maxN=20,
        singleton=None,
        printInc=print_inc,
        forcedInOutput=False,
    )
    # Check that b and d are identical after sorting
    assert np.all(
        base.range(base.diff(base.sort(SSBtools.Match(b[d.columns], d))))
        == np.array([1, 1])
    )

    assert len(a._rattributes["startRow"]) == 16
