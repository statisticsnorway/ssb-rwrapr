from .renv import Renv
import rpy2.robjects.packages as rpkg


def library(env_name: str, interactive = True) -> Renv | None:
    """Load an R environment (package) into the current session."""
    try:
        return Renv(env_name, interactive=interactive)
    except rpkg.PackageNotInstalledError:
        if not interactive:
            return None
        else:
            raise rpkg.PackageNotInstalledError


def importr(env_name: str, interactive = True) -> Renv | None:
    """Load an R environment (package) into the current session."""
    return library(env_name, interactive=interactive)
