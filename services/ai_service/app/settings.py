from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Base settings."""

    ai_openai_azure_key: str
    ai_openai_azure_endpoint: str
    ai_openai_azure_model: str = "gpt-4"

    ai_embedding_azure_key: str
    ai_embedding_azure_endpoint: str
    ai_embedding_azure_model: str = "text-embedding-ada-002"

    ai_elasticsearch_url: str

    ai_rabbit_hostname: str
    ai_rabbit_port: int
    ai_rabbit_username: str
    ai_rabbit_password: str

    ai_rabbit_pool_size: int = 5
    ai_rabbit_channel_pool_size: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()  # type: ignore
