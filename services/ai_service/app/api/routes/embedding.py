from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncAzureOpenAI
from app.api.dtos.dtos import RestaurantEmbeddingInputDTO, RestaurantInputDTO
from app.services.azure_ai.client import get_embedding_client
from app.services.azure_ai.embeddings import generate_restaurant_embedding
from app.services.es.dependencies import GetES

router = APIRouter()


@router.post("/embedding")
async def add_embedding(
    request: Request,
    input_dto: RestaurantInputDTO,
    es_client: GetES,
    embedding_client: AsyncAzureOpenAI = Depends(get_embedding_client),
) -> dict[str, RestaurantEmbeddingInputDTO]:
    """Endpoint to generate and save an embedding for a restaurant."""
    metrics = request.app.state.metrics

    try:
        # Track the embedding generation operation
        async with metrics.track_async_operation("embedding", "generation"):
            embedding = await generate_restaurant_embedding(
                input_dto=input_dto, ai_client=embedding_client, es_client=es_client
            )

            if embedding is None:
                metrics.track_error("EmbeddingGenerationError", "embedding_generation")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to generate embedding for the provided input.",
                )

        # Track successful operation
        metrics.track_embedding_request("success", duration=0)
        return {"data": embedding}

    except ValueError as e:
        metrics.track_error("ValueError", "embedding_endpoint")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        metrics.track_error("RuntimeError", "embedding_endpoint")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        metrics.track_error(type(e).__name__, "embedding_endpoint")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
