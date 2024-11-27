from openai import AsyncAzureOpenAI
from settings import settings


client = AsyncAzureOpenAI(
    api_key="B5OuMdEvWPWHmid5t05gB3WwraaOL2gzg5xImLpy73tDyuVfge74JQQJ99AKACYeBjFXJ3w3AAABACOG5hLz",
    api_version="2024-08-01-preview",
    azure_endpoint="https://skynet-420.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview",
)

embedding_client = AsyncAzureOpenAI(
    api_key=settings.embedding_azure_key,
    api_version="2023-05-15",
    azure_endpoint=settings.embedding_azure_endpoint,
)

