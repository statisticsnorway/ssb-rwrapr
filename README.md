# `ssb-wrapr-python`
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
    2. Better conversion handling for output
        - Convert ordered dictionaries (which are vectors) to numpy arrays
        - Convert ordered dictionaries (which are lists) to dictionaries
        - Convert lists (which are vectors) to vectors
        - Convert lists (which are lists) to lists
        - S4 CLASSES ARE TRICKY!
    3. Better conversion handling for input!
        - S4 CLASSES ARE TRICKY
        - Look at the Matrix library
            - rpy2-Matrix on GitHub (abandoned repo, but might be helpful)
    4. Refactor modules, into seperate files 
        - Look at the Matrix library
            - rpy2-Matrix on GitHub (abandoned repo, but might be helpful)
    5. Better warning handling (this will likely be tricky)
        - Sometimes we will get datatypes which are incompatible, 
            e.g., warning accompanied by 
    6. Add option to return as R-object?
    8. Add autcomplete for un-indexed functions?
    9. Load some requested functions of import?
    10. Better documentation!
    11. Add some datatypes?
        - rlist? 
            - it is just a list with a dict[label: str, index: int]
            - boolean indexing?
        - wrapper for R-objects using a intuitive Python-Api, with an option
            to return as python object!
