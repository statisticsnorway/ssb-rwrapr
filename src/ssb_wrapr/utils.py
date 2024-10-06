import rpy2.rinterface_lib.callbacks
import termcolor as tc


def pinfo(message: str, verbose: bool = True) -> None:
    if verbose:
        print(tc.colored("Info", "green") + " | " + message)


class ROutputCapture:
    def __init__(self) -> None:
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self.stdout_orig = None
        self.stderr_orig = None

    def capture_r_output(self) -> None:
        def add_to_stdout(line: str) -> None:
            self.stdout.append(line)

        def add_to_stderr(line: str) -> None:
            self.stderr.append(line)

        self.stdout_orig = rpy2.rinterface_lib.callbacks.consolewrite_print
        self.stderr_orig = rpy2.rinterface_lib.callbacks.consolewrite_warnerror
        rpy2.rinterface_lib.callbacks.consolewrite_print = add_to_stdout
        rpy2.rinterface_lib.callbacks.consolewrite_warnerror = add_to_stderr

    def reset_r_output(self) -> None:
        rpy2.rinterface_lib.callbacks.consolewrite_print = self.stdout_orig
        rpy2.rinterface_lib.callbacks.consolewrite_warnerror = self.stderr_orig
