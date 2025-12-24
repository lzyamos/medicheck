from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Medicheck API"
    ENV: str = "dev"

    # JWT
    JWT_SECRET: str = Field(..., min_length=32)
    JWT_ISSUER: str = "medicheck"
    JWT_AUDIENCE: str = "medicheck-web"
    JWT_EXPIRES_MINUTES: int = 60

    # Database
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
