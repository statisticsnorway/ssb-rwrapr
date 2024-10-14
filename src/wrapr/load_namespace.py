import warnings

import rpy2.robjects as ro
import rpy2.robjects.packages as rpkg

from .utils import ROutputCapture
from .utils import pinfo


def load_base_envs() -> dict[str, rpkg.InstalledSTPackage | rpkg.InstalledPackage]:
    # set options for global environment
    rbase = try_load_namespace("base", verbose=False)
    rMatrix = try_load_namespace("Matrix", verbose=False)
    rutils = try_load_namespace("utils", verbose=False)
    return {"base": rbase, "Matrix": rMatrix, "utils": rutils}


def try_load_namespace(
    namespace: str, verbose: bool = False, hide_r_ouptut=True, interactive=True
):
    if hide_r_ouptut:
        capture = ROutputCapture()
        capture.capture_r_output()
    try:
        warnings.filterwarnings("ignore")
        module: rpkg.Package = rpkg.importr(namespace)
    except rpkg.PackageNotInstalledError:
        if not interactive:
            raise

        choice = input(namespace + " not installed, do you want to install it? (y/n)\n")
        if choice[0] != "y":
            raise rpkg.PackageNotInstalledError from rpkg.PackageNotInstalledError
        pinfo("Installing package...", verbose=verbose)
        ro.r(f'install.packages("{namespace}")', print_r_warnings=False, invisible=True)
        pinfo("Package installed!", verbose=verbose)
        module: rpkg.Package = rpkg.importr(namespace)

    if hide_r_ouptut:
        capture.reset_r_output()
    return module
