# `WrapR`<img src="images/WrapR-logo.png" alt="Logo" align = "right" height="139" class="logo">
wrapr is a `python` package for using R inside of python.
It is built using `rpy2`, but attempts to be more convient to use. 
Ideally you should never have to worry about using `R` objects,
instead treating `R` functions as normal `python` functions, where the inputs
and outputs are `python` objects.

```
import wrapr as wr
import pandas as pd
import numpy as np
import pytest


dplyr = wr.library("dplyr")
dt = wr.library("datasets")

dplyr.last(x=np.array([1, 2, 3, 4]))
dplyr.last(x=[1, 2, 3, 4])


iris = dt.iris
df = dplyr.mutate(iris, Sepal = wr.lazily("round(Sepal.Length * 2, 0)"))

```

## To do:
    1. Port all test files for SSB-GaussSuppression, and SSBtools
    2. Names/Dimnames for Vectors/Arrays/Matrices
    3. Factors/Ordered Vectors
    4. Better warning handling (this will likely be tricky)
        - Sometimes we will get datatypes which are incompatible, 
            e.g., warning accompanied by 
