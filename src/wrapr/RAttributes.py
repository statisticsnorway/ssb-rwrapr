from .function_wrapper import rfunc


def get_Rattributes(x: Any) -> Any:
    foo: Callable = rfunc("attributes")
    return foo(x)
