"""All the configurations are defined here"""
import secrets
from typing import Literal, Annotated,Any
from pydantic import BeforeValidator, AnyUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_cors(v: Any) -> list[str] | str:
    """
    Function to normalize CORS ORIGINS input
    throws error if input format is invalid
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    """Setting Configurations"""
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SECRET_KEY : str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    FRONTEND_HOST : str = "https://localhost:3000"
    ENVIRONMENT : Literal["local", "staging", "production"] = "local"
    BACKEND_CORS_ORIGIN: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origin(self) -> list[str]:
        """check for cors """
        return [str(origin).rstrip('/') for origin in self.BACKEND_CORS_ORIGIN] + [
            self.FRONTEND_HOST
        ]


settings = Settings()
