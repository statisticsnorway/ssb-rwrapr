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
# # Eksempel på bruk av python-biblioteket rwrapr til å kalle R-funksjoner fra python
#
# Biblioteket [rwrapr](https://github.com/statisticsnorway/ssb-rwrapr)
# installeres via kommandoen `poetry add rwrapr`.

# %%
import numpy as np
import pandas as pd

import rwrapr as wr


# %% [markdown]
# Leser inn et datasett med pandas på vanlig måte:

# %%
df = pd.read_csv("dataset_z1.csv")
df.head()

# %% [markdown]
# ## Installering av R-pakker
# Hvis pakken ikke er installert så spør funksjonen deg om du vil installere pakken. Pakker fra CRAN installeres slik:

# %%
GaussSuppression = wr.library("GaussSuppression")

# %% [markdown]
# Pakker fra GitHub installeres som vist nedenfor. Installasjonen av Metodebiblioteket tar litt tid
# så du kan hoppe over dette steget hvis du bare kjapt vil teste at rwrapr-biblioteket virker.
# Metodebiblioteket brukes ikke videre i denne koden.

# %%
devtools = wr.library("devtools")
devtools.install_github("statisticsnorway/ssb-metodebiblioteket")
method_library = wr.library("metodebiblioteket")

# %% [markdown]
# ## Bruk

# %%
suppressed = GaussSuppression.GaussSuppressionFromData(df, np.array([1, 2]), 3)
suppressed.sample(5, random_state=22)

# %% [markdown]
# Suppressed er en RDataFrame. For å konvertere til en pandas dataframe bruker du kommandoen to_py():

# %%
suppressed_df = suppressed.to_py()
suppressed_df.head()

# %%
