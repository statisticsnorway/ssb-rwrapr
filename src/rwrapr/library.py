import rpy2.robjects.packages as rpkg

from .renv import Renv


def library(env_name: str, interactive: bool = True) -> Renv:
    """
    Load an R environment (package) into the current Python session.

    This function attempts to load an R package and create an R environment
    using the `Renv` class. If the package is not installed and `interactive`
    is set to `False`, it returns an uninitialized `Renv` object.

    Args:
        env_name (str): The name of the R package to load.
        interactive (bool): If `True`, interactively prompts the user
            to install missing R packages. Defaults to `True`.

    Returns:
        Renv: The loaded R environment.

    Raises:
        rpkg.PackageNotInstalledError: If the R package is not installed and
            `interactive` is set to `True`.
    """
    try:
        return Renv(env_name, interactive=interactive)
    except rpkg.PackageNotInstalledError:
        if interactive:
            raise
        return Renv(None)


def importr(env_name: str, interactive: bool = True) -> Renv:
    """
    Load an R environment (package) into the current Python session.

    This function is an alias for `library()`, used to load an R package and
    create an R environment in Python using the `Renv` class.

    Args:
        env_name (str): The name of the R package to load.
        interactive (bool): If `True`, interactively prompts the user
            to install missing R packages. Defaults to `True`.

    Returns:
        Renv: The loaded R environment.
    """
    return library(env_name, interactive=interactive)
