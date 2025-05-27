from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:0yq5h3to9@localhost/base_uac"
    
    # Security
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_name: str = "UAC FastAPI"
    debug: bool = True
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings() 