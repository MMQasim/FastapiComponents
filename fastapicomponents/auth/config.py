from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # 🔐 Secret & Algorithm
    AUTH_SECRET_KEY: str = Field(
        default="fallback-dev-secret",
        description="Secret key used for JWT encoding/decoding"
    )
    AUTH_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )

    # ⏱ Token Expiry Durations
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token lifespan in minutes"
    )
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token lifespan in days"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
        
