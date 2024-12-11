from openai import AsyncAzureOpenAI
from app.settings import settings


def get_chat_client() -> AsyncAzureOpenAI:
    """Provide an OpenAI chat client."""
    return AsyncAzureOpenAI(
        api_key=settings.openai_azure_key,
        api_version="2024-08-01-preview",
        azure_endpoint=settings.openai_azure_endpoint,
    )


def get_embedding_client() -> AsyncAzureOpenAI:
    """Provide an OpenAI embedding client."""
    return AsyncAzureOpenAI(
        api_key=settings.embedding_azure_key,
        api_version="2023-05-15",
        azure_endpoint=settings.embedding_azure_endpoint,
    )
