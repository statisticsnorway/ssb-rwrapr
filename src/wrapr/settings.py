class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(**kwargs)
        return cls._instance

    def _initialize(self):
        self.Rview = False

    def set_Rview(self, rview: bool):
        self.Rview = rview


settings = Settings()
