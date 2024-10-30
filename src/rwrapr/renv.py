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
    """
    Represents an R environment in Python for interacting with R packages, functions, and datasets.
    Functions and datasets are loaded/attached to the environment dynamically. If a function or dataset is not found in the environment,
    it is searched for in the global R environment.

    Attributes:
        __base_lib (rpkg.Package | None): The loaded R package.
        __rfuncs (set[str] | None): The set of R functions available in the environment.
        __rdatasets (set[str] | None): The set of R datasets available in the environment.
        NULL (Any): Equivalent to R's `NULL`.
        NA (Any): Equivalent to R's `NA`.
        NaN (Any): Equivalent to R's `NaN`.
        Inf (Any): Equivalent to R's `Inf`.
        nInf (Any): Equivalent to R's `-Inf`.
    """

    def __init__(self, env_name: str | None, interactive: bool = True) -> None:
        """
        Initializes the R environment by loading the specified R package and its associated functions and datasets.

        Args:
            env_name (str | None): The name of the R package to load. If `None` or an empty string, the environment is not initialized.
            interactive (bool): If True, prompts the user to install missing R packages. Defaults to True.
        """
        if (env_name is None) or (env_name == ""):
            self.__base_lib: rpkg.Package | None = None
            self.__rfuncs: set[str] | None = None
            self.__rdatasets: set[str] | None = None
            return

        pinfo("Loading packages...", verbose=True)
        self.__set_base_lib(
            try_load_namespace(env_name, verbose=True, interactive=interactive)
        )

        funcs, datasets = get_assets(env_name, module=self.__base_lib)
        self.__set_rfuncs(funcs)
        self.__set_rdatasets(datasets)

        # Constants
        self.NULL = ro.NULL
        self.NA = ro.NA_Logical
        self.NaN = ro.r("NaN")
        self.Inf = ro.r("Inf")
        self.nInf = ro.r("-Inf")

        pinfo("Done!", verbose=True)

    def __set_base_lib(self, rpkg_: rpkg.Package) -> None:
        """
        Sets the base R package for the environment.

        Args:
            rpkg_ (rpkg.Package): The R package to set.
        """
        self.__base_lib = rpkg_

    def __set_rfuncs(self, funcs: set[str]) -> None:
        """
        Sets the available R functions for the environment.

        Args:
            funcs (set[str]): A set of R function names.
        """
        self.__rfuncs = funcs

    def __set_rdatasets(self, datasets: set[str]) -> None:
        """
        Sets the available R datasets for the environment.

        Args:
            datasets (set[str]): A set of R dataset names.
        """
        self.__rdatasets = datasets

    def __attach(self, name: str, attr: Any) -> None:
        """
        Attaches a function or dataset to the environment.

        Args:
            name (str): The name of the R object (function or dataset).
            attr (Any): The object to attach (function or dataset).
        """
        if attr is None:
            return
        setattr(self, name, attr)

    def __getattr__(self, name: str) -> Any:
        """
        Retrieves an R function or dataset from the environment, attaching it if necessary.

        Args:
            name (str): The name of the R function or dataset.

        Returns:
            Any: The R function or dataset, if found.

        Raises:
            ValueError: If the environment is not correctly initialized or if the object is not found.
        """
        if self.__rfuncs is None or self.__rdatasets is None:
            raise ValueError("Renv is not correctly initialized")

        capture = ROutputCapture()
        capture.capture_r_output()

        if name in self.__rfuncs:
            fun: Callable[..., RReturnType] = wrap_rfunc(
                getattr(self.__base_lib, name), name=name
            )
            self.__attach(name=name, attr=fun)
            capture.reset_r_output()
        elif name in self.__rdatasets:
            self.__attach(name=name, attr=fetch_data(name, self.__base_lib))
            capture.reset_r_output()
        else:
            rfun: Callable[..., RReturnType] = rfunc(name)
            self.__attach(name=name, attr=rfun)

        return getattr(self, name)

    def __function__(self, name: str, expr: str) -> None:
        """
        Attaches an R function to the environment.

        Args:
            name (str): The name of the function.
            expr (str): The R expression to create the function.

        Raises:
            ValueError: If the R expression does not correspond to a function.
        """
        rfun: Callable[..., Any] | None = ro.r(
            expr, invisible=True, print_r_warnings=False
        )
        if rfun is None:
            raise ValueError(f"R object: {expr} is not a function")

        # Attach to the global namespace
        rcall(f"{name} <- {expr}")
        pyfunc: Callable[..., RReturnType] = wrap_rfunc(rfun, name=name)
        self.__attach(name=name, attr=pyfunc)

    def function(self, expr: str) -> Callable[..., Any]:
        """
        Creates a Python function from an R expression.

        Args:
            expr (str): The R expression to convert into a function.

        Returns:
            Callable[..., Any]: A Python function equivalent to the R function.

        Raises:
            ValueError: If the R expression does not correspond to a function.
        """
        rfun: Callable[..., Any] | None = ro.r(
            expr, invisible=True, print_r_warnings=False
        )
        if rfun is None:
            raise ValueError(f"R object: {expr} is not a function")

        pyfunc: Callable[..., RReturnType] = wrap_rfunc(rfun, name=None)
        return pyfunc

    def print(self, x: Any) -> None:
        """
        Prints an object as it would be printed in R.

        Args:
            x (Any): The object to print.
        """
        foo: Callable[..., RReturnType] = rfunc(
            """
            function(x, ...) {
                paste(utils::capture.output(print(x, ...)), collapse = "\n")
            }
            """
        )
        print(foo(x))

    def rclass(self, x: Any) -> RReturnType:
        """
        Gets the class of an object as it would be in R.

        Args:
            x (Any): The object to get the class of.

        Returns:
            RReturnType: The class of the object as in R.
        """
        foo: Callable[..., RReturnType] = rfunc("class")
        return foo(x)

    def reval(self, expr: str, rview: bool) -> Any:
        """
        Evaluates an R expression.

        Args:
            expr (str): The R expression to evaluate.
            rview (bool): If True, returns the result as an RView object. Defaults to False.

        Returns:
            Any: The result of the R expression, depends on rview argument and setting.
        """
        rview = rview or settings.rview_mode

        r_object: Any = ro.r(expr, invisible=True, print_r_warnings=False)

        if rview:
            return RView(r_object)
        else:
            return convert_r2py(r_object)


def fetch_data(
    dataset: str, module: rpkg.Package | None
) -> pd.DataFrame | RView | None:
    try:
        r_object = rpkg.data(module).fetch(dataset)[dataset]

        if settings.rview_mode:
            return RView(r_object)
        else:
            result = convert_r2py(r_object)
            if not isinstance(result, pd.DataFrame):
                raise ValueError(f"The provided dataset: {dataset} is not a DataFrame")
            return result

    except (KeyError, Exception):
        return None


def get_assets(env_name: str, module: rpkg.Package | None) -> tuple[set[str], set[str]]:
    rcode: str = f'library({env_name}); ls("package:{env_name}")'
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: set[str] = {
        x.replace(".", "_")
        for x in set(ro.r(rcode, invisible=True, print_r_warnings=False))
    }

    pyattrs: set[str] = set(dir(module))
    # return: funcs, other-assets
    return rattrs & pyattrs, rattrs - pyattrs
