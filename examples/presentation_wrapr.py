# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: ssb-rwrapr
#     language: python
#     name: ssb-rwrapr
# ---

# %% [markdown]
# # Prikking av Data

# %% [markdown]
# Importere `WrapR` og `Numpy`

# %%
import numpy as np

import rwrapr as wr


# %% [markdown]
# Importere `R`-pakker (`GaussSuppression` og `SSBtools`)

# %%
GaussSuppression = wr.library("GaussSuppression")
SSBtools = wr.library("SSBtools")

# %% [markdown]
# Åpne et testdataset fra `SSBtools`

# %%
z1 = SSBtools.SSBtoolsData("z1")
z1.head()

# %% [markdown]
# Prikke data med `GaussSuppression`

# %%
suppressed = GaussSuppression.GaussSuppressionFromData(z1, np.array([1, 2]), 3)
suppressed.sample(5, random_state=22)

# %% [markdown]
# # Hvis du ikke liker `Python`
# Hvis du virkelig hater `Python` og i steden vil skrive `R`-kode, så kan du gjøre det også...

# %%
R = wr.library("base")  # Importer baselibrariettil R

# %% [markdown]
# Du trenger ikke å bruke et `Numpy.ndarray`, men kan heller bruke `c()`

# %%
R.c(1, 2, 3)

# %% [markdown]
# Du trenger heller ikke å bruke en `Pandas.DataFrame`, og kan heller bruke `data.frame`

# %%
R.data_frame(a=R.c(1, 2, 3), b=R.c(4, 5, 6))

# %% [markdown]
# Hvis du har et kult datasett i `R`, kan du også hente det ut i `Python`

# %%
datasets = wr.library("datasets")
datasets.iris.head()
