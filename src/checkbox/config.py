from pydantic_settings import BaseSettings, SettingsConfigDict

POSTGRES_DSN_TEMPLATE = (
    "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
)


class PostgresSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DATABASE: str

    @property
    def url(self) -> str:
        return POSTGRES_DSN_TEMPLATE.format(
            user=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            database=self.DATABASE,
        )


class SQLAlchemySettings(BaseSettings):
    ECHO: bool = True


class AuthSettings(BaseSettings):
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    postgres: PostgresSettings
    sqlalchemy: SQLAlchemySettings
    auth: AuthSettings
