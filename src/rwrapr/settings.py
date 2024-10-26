from __future__ import annotations


class Settings:
    _instance: Settings | None = None  # Singleton instance of the class

    def __new__(cls) -> Settings:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "rview_mode"):  # Check if already initialized
            self.rview_mode = False

    def set_rview_mode(self, rview_mode: bool) -> None:
        """Set the rview_mode attribute to the specified value.

        This method updates the `rview_mode` attribute to control whether the
        RView mode is enabled or disabled. If `True`, Rview mode is enabled;
        if `False`, Rview mode is disabled. If Rview is True, then only Views of
        R objects will be displayed in the console. Otherwise, `rwrapr` will try
        to convert the R object to a Python object and display it.

        Args:
            rview_mode: A boolean value indicating whether to enable (True)
                or disable (False) RView mode.
        """
        self.rview_mode = rview_mode


# Singleton instance of Settings
settings: Settings = Settings()
