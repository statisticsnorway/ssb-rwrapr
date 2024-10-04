import rpy2.robjects.packages as rpkg

from .renv import Renv


def library(env_name: str, interactive=True) -> Renv | None:
    try:
        return Renv(env_name, interactive=interactive)
    except rpkg.PackageNotInstalledError:
        if not interactive:
            return None
        else:
            raise rpkg.PackageNotInstalledError


def importr(env_name: str, interactive=True) -> Renv | None:
    return library(env_name, interactive=interactive)
