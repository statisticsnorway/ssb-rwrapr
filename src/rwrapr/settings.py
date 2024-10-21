from typing import Any
from typing import Optional


class Settings:
    _instance: Optional["Settings"] = None  # Singleton instance of the class
    Rview: bool  # Boolean attribute to store Rview setting

    def __new__(cls, *args: Any, **kwargs: Any) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(**kwargs)
        return cls._instance

    def _initialize(self, **kwargs: Any) -> None:
        self.Rview = False  # Initialize the Rview attribute to False

    def set_Rview(self, rview: bool) -> None:
        """
        Set the Rview attribute to the specified value.

        This method updates the `Rview` attribute to control whether the
        Rview mode is enabled or disabled. If `True`, Rview mode is enabled;
        if `False`, Rview mode is disabled. If Rview is True, then only Views of
        R objects will be displayed in the console. Otherwise, `rwrapr` will try
        to convert the R object to a Python object and display it.

        Args:
            rview (bool): A boolean value indicating whether to enable (True)
                or disable (False) Rview mode.
        """
        self.Rview = rview  # Set the Rview attribute


# Singleton instance of Settings
settings: Settings = Settings()
