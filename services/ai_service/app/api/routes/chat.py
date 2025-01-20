from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncAzureOpenAI
from app.services.es.dependencies import GetES
from app.api.dtos.dtos import UserPrompt, UserRequestDTO
from app.services.azure_ai.chat import generate_chat_response
from app.services.azure_ai.client import get_chat_client, get_embedding_client
from app.services.azure_ai.embeddings import search_embedding

router = APIRouter()


@router.post("/chat")
async def chat_with_embeddings(
    request: Request,
    input_dto: UserRequestDTO,
    es_service: GetES,
    chat_client: AsyncAzureOpenAI = Depends(get_chat_client),
    embedding_client: AsyncAzureOpenAI = Depends(get_embedding_client),
) -> dict[str, Any]:
    """Endpoint for generating a response based on user input and embeddings."""
    metrics = request.app.state.metrics

    try:
        # Track embedding search operation
        async with metrics.track_async_operation("embedding"):
            result = await search_embedding(
                input_dto=input_dto,
                client=embedding_client,
                es_service=es_service,
                limit=2,
            )

            if not result:
                metrics.track_error("NotFoundError", "chat_embeddings_search")
                raise HTTPException(status_code=404, detail="No embeddings found.")

        # Track elasticsearch operations
        async with metrics.track_async_operation("elasticsearch", "search"):
            prompt = UserPrompt(user_input=input_dto.user_input, restaurants=result)
            print(prompt)

        # Track chat generation operation
        async with metrics.track_async_operation("embedding", "chat_generation"):
            response = await generate_chat_response(prompt=prompt, client=chat_client)

        return {"data": response}

    except ValueError as e:
        metrics.track_error("ValueError", "chat_endpoint")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        metrics.track_error("RuntimeError", "chat_endpoint")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        metrics.track_error(type(e).__name__, "chat_endpoint")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
