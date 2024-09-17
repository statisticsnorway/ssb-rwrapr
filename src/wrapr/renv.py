import pandas as pd
import numpy as np
import warnings

import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
import rpy2.rlike.container as rcnt
import rpy2.robjects.packages as rpkg

from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, OrderedDict, Set, Tuple
from copy import Error
from rpy2.robjects import pandas2ri, numpy2ri

from .load_namespace import load_base_envs, try_load_namespace
from .utils import ROutputCapture, pinfo
from .function_wrapper import rfunc, wrap_rfunc # wrap_rfunc should perhaps be its own module
from .rutils import rcall
from .convert_r2py import convert_r2py, Robject
from .settings import Settings, settings


class Renv:
    def __init__(self, env_name):
        pinfo("Loading packages...", verbose=True)
        # self.__Renvironments__ = load_base_envs()
        self.__set_base_lib__(try_load_namespace(env_name, verbose=True))
        
        funcs, datasets = get_assets(env_name, module=self.__base_lib__)
        self.__setRfuncs__(funcs) 
        self.__setRdatasets__(datasets) 

        pinfo("Done!", verbose=True)
        return None
  
    def __set_base_lib__(self, rpkg: rpkg.Package) -> None:
        self.__base_lib__ = rpkg

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
            fun: Callable = wrap_rfunc(getattr(self.__base_lib__, name), name=name)
            self.__attach__(name=name, attr=fun)
            capture.reset_r_output()
            return getattr(self, name)
        elif name in self.__Rdatasets__:
            self.__attach__(name=name, attr=fetch_data(name, self.__base_lib__))
            capture.reset_r_output()
            return getattr(self, name)
        else: 
            warnings.warn("fetching assets from R-environment directly, this feature is not finished yet")
            fun: Callable = rfunc(name) # in the future this should also work for datasets
            # add error handling for corrupt function, getting stuck to Renv
            self.__attach__(name=name, attr=fun)
            return getattr(self, name)

    def __function__(self, name: str, expr: str) -> None:
        rfunc: Callable | Any = ro.r(expr, invisible=True,
                                     print_r_warnings=False)
        # also attach to global namespace
        rcall(f"{name} <- {expr}")
        pyfunc: Callable = wrap_rfunc(rfunc, name=name)

        self.__attach__(name=name, attr=pyfunc)

    def function(self, expr: str) -> Callable:
        rfunc: Callable | Any = ro.r(expr, invisible=True,
                                     print_r_warnings=False)
        pyfunc: Callable = wrap_rfunc(rfunc, name=None)
        if not callable(pyfunc):
            raise ValueError("R object is not a function")
        return pyfunc
    
    # def attributes(self, py_object: Any) -> Any:
    #     return py_object.__Rattributes__

    # def attr(self, py_object: Any, key: str) -> Any:
    #     attributes = self.attributes(py_object)
    #     try:
    #         return attributes[key]
    #     except TypeError:
    #         return attributes


def fetch_data(dataset: str, module: rpkg.Package) -> pd.DataFrame | Robject | None:
    try:
        r_object = rpkg.data(module).fetch(dataset)[dataset]

        if settings.Rview:
            return Robject(r_object)
        else:
            return convert_r2py(r_object)

    except KeyError:
        return None
    except:
        return None

        
def get_assets(env_name: str, module: rpkg.Package) -> Tuple[Set[str], Set[str]]:
    rcode: str = f"library({env_name}); ls(\"package:{env_name}\")"
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: Set[str] = {x.replace(".", "_") for x in 
                        set(ro.r(rcode, invisible=True, 
                                 print_r_warnings=False))}

    pyattrs: Set[str] = set(dir(module))
    # return: funcs, other-assets
    return (rattrs & pyattrs, rattrs - pyattrs)
