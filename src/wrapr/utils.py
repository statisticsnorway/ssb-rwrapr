import termcolor as tc
import rpy2.rinterface_lib.callbacks


def pinfo(message: str, verbose = True) -> None:
    if verbose:
        print(tc.colored('Info', 'green') + " | " + message)


class ROutputCapture:
    def __init__(self):
        self.stdout = []
        self.stderr = []
        self.stdout_orig = None
        self.stderr_orig = None

    def capture_r_output(self):
        """Redirects R console output to Python lists."""
        # Define custom functions to capture output
        def add_to_stdout(line): self.stdout.append(line)
        def add_to_stderr(line): self.stderr.append(line)
        
        # Keep original callbacks
        self.stdout_orig = rpy2.rinterface_lib.callbacks.consolewrite_print
        self.stderr_orig = rpy2.rinterface_lib.callbacks.consolewrite_warnerror
        
        # Replace with custom callbacks
        rpy2.rinterface_lib.callbacks.consolewrite_print = add_to_stdout
        rpy2.rinterface_lib.callbacks.consolewrite_warnerror = add_to_stderr

    def reset_r_output(self):
        """Resets the R output callbacks to their original state."""
        rpy2.rinterface_lib.callbacks.consolewrite_print = self.stdout_orig
        rpy2.rinterface_lib.callbacks.consolewrite_warnerror = self.stderr_orig


