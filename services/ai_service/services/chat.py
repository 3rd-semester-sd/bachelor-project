from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_postgres import PGVector
from langchain.embeddings import OpenAIEmbeddings


async def search_and_generate_response(user_query: str, session):
    # Initialize PGVector search
    embedding_model = OpenAIEmbeddings(openai_api_key="your_openai_api_key")
    vector_store = PGVector(
        collection_name="restaurant_data",
        connection_string="postgresql+asyncpg://ai:ai@localhost/pg-ai-service",
        embedding_function=embedding_model,
    )

    # Search relevant context
    results = vector_store.similarity_search(user_query, k=3)
    context = "\n".join([result["description"] for result in results])

    # Create Chat Prompt
    prompt = PromptTemplate(
        input_variables=["context", "query"],
        template="""
        You are an assistant providing information about restaurants. 
        Given the following context, answer the user's query.

        Context:
        {context}

        Query:
        {query}
        """,
    )

    llm = ChatOpenAI(openai_api_key="your_openai_api_key")
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(context=context, query=user_query)

    return response
