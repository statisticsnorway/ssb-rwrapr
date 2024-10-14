# WrapR

[![PyPI](https://img.shields.io/pypi/v/ssb-wrapr.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/ssb-wrapr.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/ssb-wrapr)][pypi status]
[![License](https://img.shields.io/pypi/l/ssb-wrapr)][license]

[![Documentation](https://github.com/statisticsnorway/ssb-wrapr/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/statisticsnorway/ssb-wrapr/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_ssb-wrapr&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_ssb-wrapr&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/ssb-wrapr/
[documentation]: https://statisticsnorway.github.io/ssb-wrapr
[tests]: https://github.com/statisticsnorway/ssb-wrapr/actions?workflow=Tests
[sonarcov]: https://sonarcloud.io/summary/overall?id=statisticsnorway_ssb-wrapr
[sonarquality]: https://sonarcloud.io/summary/overall?id=statisticsnorway_ssb-wrapr
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/

## Features

<img src="images/WrapR-logo.png" alt="Logo" align = "right" height="139" class="logo">
`WrapR` is a `python` package for using R inside of python.
It is built using `rpy2`, but attempts to be more convient to use.
Ideally you should never have to worry about using `R` objects,
instead treating `R` functions as normal `python` functions, where the inputs
and outputs are `python` objects.

```python
import wrapr as wr
import pandas as pd
import numpy as np

dplyr = wr.library("dplyr")
dt = wr.library("datasets")

dplyr.last(x=np.array([1, 2, 3, 4]))
dplyr.last(x=[1, 2, 3, 4])


iris = dt.iris
df = dplyr.mutate(iris, Sepal = wr.lazily("round(Sepal.Length * 2, 0)"))
```

## To do

    1. Port all test files for SSB-GaussSuppression, and SSBtools
    2. Names/Dimnames for Vectors/Arrays/Matrices
    3. Factors/Ordered Vectors
    4. Better warning handling (this will likely be tricky)
        - Sometimes we will get datatypes which are incompatible,
            e.g., warning accompanied by

## Requirements

- TODO

## Installation

You can install _WrapR_ via [pip] from [PyPI]:

```console
pip install rwrapr
```

## Usage

Please see the [Reference Guide] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_WrapR_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/statisticsnorway/ssb-wrapr/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/statisticsnorway/ssb-wrapr/blob/main/LICENSE
[contributor guide]: https://github.com/statisticsnorway/ssb-wrapr/blob/main/CONTRIBUTING.md
[reference guide]: https://statisticsnorway.github.io/ssb-wrapr/reference.html
