from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Base settings."""

    ai_database_url: str = "postgresql+asyncpg://ai:ai@localhost/pg-ai-service"
    ai_openai_azure_key: str = ""
    ai_openai_azure_endpoint: str = ""
    ai_openai_azure_model: str = "gpt-4"

    ai_embedding_azure_key: str = ""
    ai_embedding_azure_endpoint: str = ""
    ai_embedding_azure_model: str = "text-embedding-ada-002"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
