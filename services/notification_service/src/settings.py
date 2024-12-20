import pathlib
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings
from yarl import URL

PREFIX = "NOTIFICATION_SERVICE_"

DOTENV = pathlib.Path(__file__).parent.parent / ".env"


class BaseSettings(PydanticBaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    def __repr__(self) -> str:
        """Return settings as a string."""
        return f"{self.__class__.__name__}({self.model_dump()})"


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


class MailgunSettings(BaseSettings):
    """Configuration for Mailgun."""

    api_key: SecretStr = SecretStr("")
    from_email: str = ""
    domain: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{PREFIX}MAILGUN_",
    )


class Settings(BaseSettings):
    """Settings for the notification service."""

    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False

    rabbit: RabbitMQSettings = RabbitMQSettings()
    mailgun: MailgunSettings = MailgunSettings()

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_prefix=PREFIX,
    )


settings = Settings()
