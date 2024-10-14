from typing import Optional

class Settings:
    _instance: Optional['Settings'] = None  # Singleton instance of the class
    Rview: bool  # Boolean attribute to store Rview setting

    def __new__(cls, *args, **kwargs) -> 'Settings':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(**kwargs)
        return cls._instance

    def _initialize(self, **kwargs) -> None:
        self.Rview = False  # Initialize the Rview attribute to False

    def set_Rview(self, rview: bool) -> None:
        self.Rview = rview  # Set the Rview attribute


# Singleton instance of Settings
settings: Settings = Settings()
