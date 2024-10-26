"""WrapR."""

import warnings


warnings.simplefilter("always")

from .lazy_rexpr import Lazily
from .library import importr
from .library import library
from .load_namespace import try_load_namespace
from .rarray import RArray
from .rdataframe import RDataFrame
from .renv import Renv
from .rfactor import RFactor
from .rlist import RDict
from .rlist import RList
from .rview import RView
from .settings import Settings
from .settings import settings
from .toggle_rview import ToggleRView


__all__ = [
    "RArray",
    "RDataFrame",
    "RDict",
    "RFactor",
    "RList",
    "RView",
    "Renv",
    "Settings",
    "importr",
    "Lazily",
    "library",
    "settings",
    "try_load_namespace",
    "ToggleRView",
]
