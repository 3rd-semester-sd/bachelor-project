from loguru import logger
from openai import AsyncAzureOpenAI
from app.api.dtos.dtos import UserPrompt
from app.settings import settings

DEFAULT_TEMPERATURE = 0


async def generate_chat_response(
    prompt: UserPrompt,
    client: AsyncAzureOpenAI,
    model: str = settings.ai_openai_azure_model,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """Generate chat response from OpenAI."""

    try:
        logger.info(
            f"Generating chat response for prompt of length {len(prompt.prompt)}"
        )
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Assistant is a large language model trained by OpenAI.",
                },
                {"role": "user", "content": prompt.prompt.strip()},
            ],
            temperature=temperature,
        )
        result = response.choices[0].message.content
        logger.info(f"usage: {response.usage}")
        logger.info("Chat response successfully generated.")
        return result if result else "Nothing generated"
    except Exception as e:
        logger.error(f"Failed to generate chat response: {e}")
        raise RuntimeError("Error wlhile generating chat response.") from e
