import termcolor as tc


def pinfo(message: str, verbose: bool = True) -> None:
    if verbose:
        print(tc.colored("Info", "green") + " | " + message)
