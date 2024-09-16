import wrapr as wr
import numpy as np
import pandas as pd
import pytest

base = wr.importr("base")
GaussSuppression = wr.importr("GaussSuppression")
SSBtools = wr.importr("SSBtools")

def test_GaussSuppressDec_and_more():
    base.set_seed(123)
    z2 = SSBtools.SSBtoolsData("z2")
    z2["y1"] = base.runif(base.nrow(z2))
    z2["y2"] = base.runif(base.nrow(z2))
    printInc = False

    # Error here if overlapping freqVar, numVar, weightVar not treated correctly.
    a = GaussSuppression.GaussSuppressDec(z2, formula = "~region * fylke * kostragr * hovedint",
                                          freqVar = "ant", protectZeros = False, maxN = 2, 
                                          numVar = np.array(["y1", "y2", "ant"]), 
                                          weightVar = "y1", printInc = printInc)
    # a[["primary", "suppressed", 
    #  "isPublish", "isInner"]] = a[["primary", "suppressed", 
    #                                "isPublish", "isInner"]].astype("bool")
    a2 = GaussSuppression.GaussSuppressDec(z2, formula = wr.lazily("~region * fylke * kostragr * hovedint"), # this also works
                                           freqVar = "ant", protectZeros = False, maxN = 2, 
                                           numVar = np.array(["y1", "y2", "ant"]), 
                                           weightVar = "y1", printInc = printInc)

     # Recalculate suppression from decimals. "kostragr" not included. 
    b = GaussSuppression.SuppressionFromDecimals(a.loc[a["isInner"].astype("bool"), :],
                                                 hierarchies = SSBtools.FindDimLists(z2[["region", "fylke", "hovedint"]]), 
                                                 freqVar = "ant", decVar = "freqDec", printInc = printInc)
    # b[["primary", "suppressed"]] = b[["primary", "suppressed"]].astype("bool")

    # Special case where all suppressions found in suppressedData.   
    d = GaussSuppression.AdditionalSuppression(z2, suppressedData = a, 
                                               dimVar = np.array(["region", "fylke", "hovedint"]), 
                                               freqVar = "ant", maxN = 20, singleton = None, 
                                               printInc = printInc, forcedInOutput = False)
    # d[["primary", "suppressed"]] = d[["primary", "suppressed"]].astype("bool")
    # Check that b and d are identical after sorting 
    assert np.all(base.range(base.diff(base.sort(SSBtools.Match(b[d.columns], d))))
                  == np.array([1, 1]))
  
    # Check that startRow attribute exists
    # assert base.length(base.attr(a, "startRow")) == 16
    # we need to write our own convertion i think
    # perhaps something like this...
    GaussSuppression.__function__("attr_wrap", """
        function(f, ...) {
            result <- f(...)
            attributes <- attributes(result)
            list(result = result, attributes = attributes)
            }
        """)
    a3 = GaussSuppression.attr_wrap(f=wr.lazily("GaussSuppressDec"), 
                   data=z2, formula = wr.lazily("~region * fylke * kostragr * hovedint"), # this also works
                   freqVar = "ant", protectZeros = False, maxN = 2, 
                   numVar = np.array(["y1", "y2", "ant"]), 
                   weightVar = "y1", printInc = printInc)
    assert len(a3["attributes"]["startRow"]) == 16
