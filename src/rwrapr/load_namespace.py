import warnings

import rpy2.robjects as ro
import rpy2.robjects.packages as rpkg

from .utils import pinfo


def load_base_envs() -> (
    dict[str, rpkg.InstalledSTPackage | rpkg.InstalledPackage | rpkg.Package]
):
    # set options for global environment
    rbase = try_load_namespace("base", verbose=False)
    rmatrix = try_load_namespace("Matrix", verbose=False)
    rutils = try_load_namespace("utils", verbose=False)
    return {"base": rbase, "Matrix": rmatrix, "utils": rutils}


def try_load_namespace(
    namespace: str,
    lib_loc: str | None = None,
    verbose: bool = False,
    interactive: bool = True,
) -> rpkg.Package:

    try:
        warnings.filterwarnings("ignore")
        module: rpkg.Package = rpkg.importr(namespace, lib_loc=lib_loc)
    except rpkg.PackageNotInstalledError:
        if not interactive:
            raise

        choice = input(namespace + " not installed, do you want to install it? (y/n)\n")
        if choice[0] != "y":
            raise rpkg.PackageNotInstalledError from rpkg.PackageNotInstalledError
        pinfo("Installing package...", verbose=verbose)
        ro.r(f'install.packages("{namespace}")', print_r_warnings=False, invisible=True)
        pinfo("Package installed!", verbose=verbose)
        module = rpkg.importr(namespace)

    return module
