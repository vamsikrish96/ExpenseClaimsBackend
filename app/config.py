from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
import secrets


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_CLAIM_AMOUNT: float = 100000
    MIN_CLAIM_AMOUNT: float = 0.01
    HIGH_VALUE_THRESHOLD: float = 10000
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"])


settings = Settings()
