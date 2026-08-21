from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpenProtecteur"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = False

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    test_postgres_db: str = "openprotecteurdb_test"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def build_database_url(self, database_name: str) -> str:
        username = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)

        return (
            f"postgresql+psycopg://{username}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{database_name}"
        )

    @computed_field
    @property
    def database_url(self) -> str:
        return self.build_database_url(self.postgres_db)

    @computed_field
    @property
    def test_database_url(self) -> str:
        return self.build_database_url(self.test_postgres_db)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
