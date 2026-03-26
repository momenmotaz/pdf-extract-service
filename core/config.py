import os

class Settings:
    PROJECT_NAME: str = "Production PDF Extractor"
    VERSION: str = "1.0.0"
    DEBUG: str = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

settings = Settings()
