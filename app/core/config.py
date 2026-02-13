"""All the configurations are defined here"""
from pathlib import Path
import secrets
from typing import Literal, Annotated,Any
from pydantic import BeforeValidator, AnyUrl, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


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
        env_file=BASE_DIR/'.env',
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

    POSTGRES_SERVER : str
    POSTGRES_PORT : int
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_DB : str

    @computed_field
    @property
    def SQLALCHEMY_POSTGRES_URL(self) -> PostgresDsn:
        """Function to build a sqlalchemy db url"""
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )
    LLM_MODEL_NAME: str
    LLM_API_KEY: str
    EMBEDDING_MODEL_NAME: str
    QDRANT_DB_COLLECTION: str
    QDRANT_DB_API_KEY: str
    QDRANT_DB_HOST : str

settings = Settings()
