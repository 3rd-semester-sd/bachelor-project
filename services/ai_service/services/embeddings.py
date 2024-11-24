from langchain.embeddings import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert


async def generate_and_store_embedding(
    name: str, description: str, session: AsyncSession
):
    embedding_model = OpenAIEmbeddings(openai_api_key="your_openai_api_key")
    embedding = embedding_model.embed_query(description)

    query = insert(restaurant_data).values(
        name=name, description=description, embedding=embedding
    )
    await session.execute(query)
    await session.commit()
