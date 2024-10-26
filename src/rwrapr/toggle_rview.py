from types import TracebackType

from .settings import settings


class ToggleRView:
    """
    A context manager to toggle the Rview setting within a `with` block.

    This class enables toggling of the Rview setting on entry and exit from
    the context block. It sets the Rview setting to a specified temp_state when
    entering the block, and reverts it when exiting the block.

    Attributes:
        temp_state (bool): The temp_state to set for the Rview mode when entering the block.
    """

    def __init__(self, temp_state: bool) -> None:
        """
        Initializes the ToggleRView context manager with the specified Rview temp_state.

        Args:
            temp_state (bool): The temp_state to set for the Rview mode when entering
                the context block.
        """
        self.orig_state = settings.rview_mode
        self.temp_state = temp_state

    def __enter__(self) -> None:
        """
        Set the Rview mode to the specified temp_state when entering the context block.

        This method is called automatically when the `with` block is entered,
        and it updates the Rview mode to the given temp_state.
        """
        settings.set_rview_mode(self.temp_state)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """
        Revert the Rview mode when exiting the context block, considering exceptions.

        This method is called automatically when the `with` block is exited. It reverts
        the Rview mode to the opposite of the temp_state set during entry. If an exception occurs
        in the block, it allows you to decide whether to suppress the exception or not.

        Args:
            exc_type (Optional[Type[BaseException]]): The type of the exception if one was raised.
            exc_val (Optional[BaseException]): The exception instance if one was raised.
            exc_tb (Optional[TracebackType]): The traceback object if an exception occurred.

        Returns:
            bool: If False, the exception is propagated. If True, the exception is suppressed.
        """
        settings.set_rview_mode(self.orig_state)

        # Check if an exception occurred
        if exc_type is not None:
            print(f"Exception of type {exc_type} occurred with temp_state: {exc_val}")
            # Return False to propagate the exception, or True to suppress it
            return False  # By returning False, the exception will not be suppressed
        return True  # No exception, normal exit
