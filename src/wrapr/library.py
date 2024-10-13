import rpy2.robjects.packages as rpkg

from .renv import Renv


def library(env_name: str, interactive: bool = True) -> Renv | None:
    """Load an R environment (package) into the current session."""
    try:
        return Renv(env_name, interactive=interactive)
    except rpkg.PackageNotInstalledError:
        if interactive:
            raise
        return None


def importr(env_name: str, interactive: bool = True) -> Renv | None:
    """Load an R environment (package) into the current session."""
    return library(env_name, interactive=interactive)
