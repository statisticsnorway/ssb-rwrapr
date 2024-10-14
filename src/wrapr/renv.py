from collections.abc import Callable
from typing import Any

import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpkg

from .convert_r2py import convert_r2py
from .function_wrapper import RReturnType
from .function_wrapper import rfunc  # wrap_rfunc should perhaps be its own module
from .function_wrapper import wrap_rfunc  # wrap_rfunc should perhaps be its own module
from .load_namespace import try_load_namespace
from .rutils import rcall
from .rview import RView
from .settings import settings
from .utils import ROutputCapture
from .utils import pinfo


class Renv:
    def __init__(self, env_name: str, interactive: bool = True) -> None:
        pinfo("Loading packages...", verbose=True)
        self.__set_base_lib__(
            try_load_namespace(env_name, verbose=True, interactive=interactive)
        )

        funcs, datasets = get_assets(env_name, module=self.__base_lib__)
        self.__setRfuncs__(funcs)
        self.__setRdatasets__(datasets)

        pinfo("Done!", verbose=True)

    def __set_base_lib__(self, rpkg_: rpkg.Package) -> None:
        self.__base_lib__ = rpkg_

    def __setRfuncs__(self, funcs: set[str]) -> None:
        self.__Rfuncs__ = funcs

    def __setRdatasets__(self, datasets: set[str]) -> None:
        self.__Rdatasets__ = datasets

    def __attach__(self, name: str, attr: Any) -> None:
        if attr is None:
            return
        setattr(self, name, attr)

    def __getattr__(self, name: str) -> Any:
        if self.__Rfuncs__ is None or self.__Rdatasets__ is None:
            raise ValueError("Renv is not correctly initialized")

        capture = ROutputCapture()
        capture.capture_r_output()

        if name in self.__Rfuncs__:
            fun: Callable[..., RReturnType] = wrap_rfunc(
                getattr(self.__base_lib__, name), name=name
            )
            self.__attach__(name=name, attr=fun)
            capture.reset_r_output()
        elif name in self.__Rdatasets__:
            self.__attach__(name=name, attr=fetch_data(name, self.__base_lib__))
            capture.reset_r_output()
        else:
            rfun: Callable[..., RReturnType] = rfunc(name)
            # in the future this should also work for datasets
            # add error handling for corrupt function, getting stuck to Renv
            self.__attach__(name=name, attr=rfun)

        return getattr(self, name)

    def __function__(self, name: str, expr: str) -> None:
        """Attach an R function to the Renv object."""
        rfun: Callable[..., Any] | None = ro.r(
            expr, invisible=True, print_r_warnings=False
        )
        if rfun is None:
            raise ValueError(f"R object: {expr} is not a function")
        # also attach to global namespace
        rcall(f"{name} <- {expr}")
        pyfunc: Callable[..., RReturnType] = wrap_rfunc(rfun, name=name)
        self.__attach__(name=name, attr=pyfunc)

    def function(self, expr: str) -> Callable[..., Any]:
        """Create a Python function from an R expression."""
        rfun: Callable[..., Any] | None = ro.r(
            expr, invisible=True, print_r_warnings=False
        )
        if rfun is None:
            raise ValueError(f"R object: {expr} is not a function")
        pyfunc: Callable[..., RReturnType] = wrap_rfunc(rfun, name=None)
        return pyfunc

    def print(self, x: Any) -> None:
        """Print an object, as it would be printed in R."""
        foo: Callable[..., RReturnType] = rfunc(
            """function(x, ...) {
            paste(utils::capture.output(print(x, ...)), collapse = "\n")
        }"""
        )
        print(foo(x))

    def rclass(self, x: Any) -> RReturnType:
        """Get the class of an object, as it would be in R."""
        foo: Callable[..., RReturnType] = rfunc(
            """function(x) {
            class(x)
        }"""
        )
        return foo(x)


def fetch_data(dataset: str, module: rpkg.Package) -> pd.DataFrame | RView | None:
    try:
        r_object = rpkg.data(module).fetch(dataset)[dataset]

        if settings.Rview:
            return RView(r_object)
        else:
            result = convert_r2py(r_object)
            if not isinstance(result, pd.DataFrame):
                raise ValueError(f"The provided dataset: {dataset} is not a DataFrame")
            return result

    except (KeyError, Exception):
        return None


def get_assets(env_name: str, module: rpkg.Package) -> tuple[set[str], set[str]]:
    rcode: str = f'library({env_name}); ls("package:{env_name}")'
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: set[str] = {
        x.replace(".", "_")
        for x in set(ro.r(rcode, invisible=True, print_r_warnings=False))
    }

    pyattrs: set[str] = set(dir(module))
    # return: funcs, other-assets
    return (rattrs & pyattrs, rattrs - pyattrs)
