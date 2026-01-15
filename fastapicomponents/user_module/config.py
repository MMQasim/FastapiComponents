from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field
from typing import List

class UserConfig(BaseSettings):
    """Defines which field uniquely identify a user."""
    DATABASE_URL:str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

@lru_cache
def get_user_config() -> UserConfig:
    return UserConfig()
#user_config:UserConfig = UserConfig()