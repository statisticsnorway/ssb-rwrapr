from _pytest.pytester import pytester
import pytest

import numpy as np
import pandas as pd
import wrapr as wr
import rpy2

SSBtools = wr.library("SSBtools")
GaussSuppression = wr.library("GaussSuppression")

num = np.array([100, 90, 10, 80, 20, 70, 30, 80, 10, 10,
                70, 10, 10, 10, 60, 20, 10, 10])
v1 = np.concatenate((np.array("v1")[np.newaxis], 
                     np.repeat(["v2", "v3", "v4"], 2),
                     np.repeat("v5", 3), 
                     np.repeat(["v6", "v7"], 4)))
sw2 = np.array([1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 
                 1, 1, 1, 2, 1, 1, 1])
sw3 = np.array([1, 0.9, 1, 2, 1, 2, 1, 2, 1, 1, 
                 2, 1, 1, 1, 2, 1, 1, 1])

d = pd.DataFrame({
    "v1"  : v1,
    "num" : num,
    "sw1" : 1,
    "sw2" : sw2,
    "sw3" : sw3
    }
  )


mm = SSBtools.ModelMatrix(d, formula = "~ v1 - 1", 
                          crossTable = True, sparse = True)

mm2 = SSBtools.ModelMatrix(d, formula = "~ v1 - 1", 
                           crossTable = True, sparse = False)

def test_Unweighted_dominance():
    p1 = GaussSuppression.DominanceRule(
            d,
            x = mm["modelMatrix"],
            crossTable = mm["crossTable"],
            numVar = "num",
            n = 2,
            k = 90
            )

    p2 = GaussSuppression.DominanceRule(
            d,
            x = mm["modelMatrix"],
            crossTable = mm["crossTable"],
            numVar = "num",
            n = 2,
            k = 90,
            sWeightVar = "sw1",
            domWeightMethod = "tauargus"
            )
    p3 = GaussSuppression.DominanceRule(
            d,
            x = mm["modelMatrix"],
            crossTable = mm["crossTable"],
            numVar = "num",
            n = 2,
            k = 90,
            sWeightVar = "sw1",
            )
    assert np.all(np.logical_and(p1 == p2["primary"], 
                                 p1 == p3["primary"]))


def test_Default_weighted_dominance():
    p = GaussSuppression.DominanceRule(
      d,
      x = mm["modelMatrix"],
      crossTable = mm["crossTable"],
      numVar = "num",
      n = 2,
      k = 90,
      sWeightVar = "sw2",
    )
      
    assert all(np.concatenate((np.array(True)[np.newaxis], 
                           np.repeat([False], 6))) == p["primary"])


def test_tauargus_dominance():
    p = GaussSuppression.DominanceRule(
            d,
            x = mm["modelMatrix"],
            crossTable = mm["crossTable"],
            numVar = "num",
            n = 2,
            k = 90,
            sWeightVar = "sw2",
            domWeightMethod = "tauargus"
            )

    assert np.all(p["primary"] == np.array([True, True, False, False, 
                                            False, False, False]))

    # Warnings dont work as they should in rpy2
    # with pytest.raises(rpy2.rinterface.RRuntimeWarning):
    #     GaussSuppression.DominanceRule(
    #       d,
    #       x = mm["modelMatrix"],
    #       crossTable = mm["crossTable"],
    #       numVar = "num",
    #       n = 2,
    #       k = 90,
    #       sWeightVar = "sw3",
    #       domWeightMethod = "tauargus"
    #     )
    
    with pytest.raises(rpy2.rinterface_lib.embedded.RRuntimeError):
        GaussSuppression.DominanceRule(
            d,
            x = mm["modelMatrix"],
            crossTable = mm["crossTable"],
            numVar = "num",
            n = 2,
            k = 90,
            charVar = "v1",
            sWeightVar = "sw1",
            domWeightMethod = "tauargus"
            )
