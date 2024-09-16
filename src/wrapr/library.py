from .renv import Renv


def library(env_name: str) -> Renv:
    return Renv(env_name)


def importr(env_name: str) -> Renv:
    return library(env_name)
