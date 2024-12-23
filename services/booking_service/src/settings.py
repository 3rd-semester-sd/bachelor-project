import pathlib
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings
from yarl import URL

PREFIX = "BOOKING_SERVICE_"

DOTENV = pathlib.Path(__file__).parent.parent / ".env"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    def __repr__(self) -> str:
        """Return settings as a string."""
        return f"{self.__class__.__name__}({self.model_dump()})"


class PGSettings(BaseSettings):
    """Configuration for database connection."""

    host: str = "localhost"

    port: int = 5432
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    database: str = "booking-db"
    pool_size: int = 15
    echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}PG_",
    )

    @property
    def url(self) -> URL:
        """Assemble database URL from settings."""

        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            path=f"/{self.database}",
        )


class PGSettingsRO(PGSettings):
    """Configuration for database connection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}PG_RO_",
    )


class RabbitMQSettings(BaseSettings):
    """Configuration for RabbitMQ."""

    host: str = "rabbitmq"
    port: int = 5672
    user: str = "user"
    password: SecretStr = SecretStr("password")
    vhost: str = "/"

    rabbit_pool_size: int = 2
    rabbit_channel_pool_size: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}RABBITMQ_",
    )

    @property
    def url(self) -> URL:
        """Assemble RabbitMQ URL from settings."""
        return URL.build(
            scheme="amqp",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password.get_secret_value(),
            path=self.vhost,
        )


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    host: str = "redis-master"
    port: int = 6379
    password: SecretStr | None = None

    @property
    def url(self) -> URL:
        """Redis URL."""
        return URL.build(
            scheme="redis",
            host=self.host,
            port=self.port,
            # password=self.password.get_secret_value() if self.password else None,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}REDIS_",
    )


class Settings(BaseSettings):
    """Settings for the booking service."""

    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False

    pg: PGSettings = PGSettings()
    pg_ro: PGSettingsRO = PGSettingsRO()

    rabbit: RabbitMQSettings = RabbitMQSettings()

    redis: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
