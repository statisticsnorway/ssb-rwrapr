import pytest
import wrapr as wr
import pandas as pd
import numpy as np

def test_RiskyIntervals():
    if wr.library("Rglpk", interactive=False) is not None:
        st = wr.library("SSBtools")
        gs = wr.library("GaussSuppression")
        bs = wr.library("base")
        
        z3 = st.SSBtoolsData("z3")
        
        upper = z3["region"].str.isupper()
        z3["region"][upper] = z3["region"][upper] + "2"        
        z3["region"][~upper] = z3["region"][~upper].str.upper() + "1"
        bs.set_seed(123)
        z3["value"] = bs.rnorm(bs.nrow(z3))**2
        
        bs.set_seed(123)
        s = bs.sample_int(bs.nrow(z3), size = 400) -1
        f = wr.lazily("~(region + fylke) * mnd2 + kostragr * hovedint * mnd")
        b = gs.SuppressDominantCells(z3.iloc[s, :], numVar = "value", n = np.array([1, 2]),
                                     k = np.array([70, 95]), formula = f, lpPackage = "Rglpk",
                                     rangePercent = 50, rangeMin = 1)
        eq = bs.as_vector(bs.table(b["suppressed_integer"])) == np.array([164, 39, 33, 3], dtype="int")
        assert np.all(eq)