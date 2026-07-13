from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/reconhive"
    jwt_secret_key: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
