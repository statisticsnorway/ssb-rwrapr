import pathlib
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
from .rlist import RDict
from .rutils import rcall
from .rview import RView
from .settings import settings
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

    def __init__(
        self, env_name: str | None, interactive: bool = True, lib_loc: str | None = None
    ) -> None:
        """
        Initializes the R environment by loading the specified R package and its associated functions and datasets.

        Args:
            env_name (str | None): The name of the R package to load. If `None` or an empty string, the environment is not initialized.
            interactive (bool): If True, prompts the user to install missing R packages. Defaults to True.
            lib_loc (str | None): The location of the R package. Defaults to None
                (Can be supplied if you are not using the default directory, e.g., if you are using renv).
        """
        if (env_name is None) or (env_name == ""):
            self.__base_lib: rpkg.Package | None = None
            self.__rfuncs: set[str] | None = None
            self.__rdatasets: set[str] | None = None
            return

        pinfo("Loading packages...", verbose=True)
        self.__set_base_lib(
            try_load_namespace(
                env_name, verbose=True, interactive=interactive, lib_loc=lib_loc
            )
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

        if name in self.__rfuncs:
            fun: Callable[..., RReturnType] = wrap_rfunc(
                getattr(self.__base_lib, name), name=name
            )
            self.__attach(name=name, attr=fun)

        elif name in self.__rdatasets:
            self.__attach(name=name, attr=fetch_data(name, self.__base_lib))

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

    def reval(self, expr: str, rview: bool | None = None) -> Any:
        """
        Evaluates an R expression.

        Args:
            expr (str): The R expression to evaluate.
            rview (bool | None): If True, returns the result as an RView object,
                else as a Python object. Defaults to None. If None,
                the value of settings.rview_mode is used.

        Returns:
            Any: The result of the R expression, depends on rview argument and setting.
        """
        rview = rview or settings.rview_mode

        r_object: Any = ro.r(expr, invisible=True, print_r_warnings=False)

        if rview:
            return RView(r_object)
        else:
            return convert_r2py(r_object)

    def rscript(
        self,
        path: str | pathlib.Path | None = None,
        code: str | None = None,
        extract: list[str] | None = None,
    ) -> None | RDict | Any:
        """
        Evaluates an R script. If extract is provided, extracts the specified objects from the R environment. If path is provided, reads the R script from the file.
        Else if code is provided, evaluates the R code directly. code and path cannot be provided at the same time.

        Args:
            path (str | pathlib.Path | None): The path to the R script to evaluate. Defaults to None.
            code (str | None): The R code to evaluate. Defaults to None.
            extract (list[str]): A list of objects to extract from the R environment.

        Raises:
            ValueError: If both path and code are provided or if neither path nor code is provided.

        Returns:
            None | RDict | Any: The extracted objects from the R environment. If no objects are extracted, returns None.
            if rview_mode is False, returns an RDict object, else returns the extracted objects as RView object.
        """

        if path is None and code is None:
            raise ValueError("Either path or code must be provided")
        if path is not None and code is not None:
            raise ValueError("Only one of path or code should be provided")

        if path is not None:
            if isinstance(path, str):
                path = pathlib.Path(path)

            with open(path) as f:
                code = f.read()

        if extract:
            list_args = [x[0] + "=" + x[1] for x in zip(extract, extract, strict=True)]
            arg_sep = ", "  # define outside the fstring to avoid the type checker error
            return_statement = f"list({arg_sep.join(list_args)})"
        else:
            return_statement = ""

        sep = "\n"
        header = "function() {"
        ending = "}"

        if (
            code is not None
        ):  # not necessary but the type checker is not able to infer this
            fun: Callable[..., Any] = self.function(
                header + sep + code + return_statement + sep + ending
            )
            return fun()
        else:
            return None


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
