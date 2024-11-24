from openai import AsyncAzureOpenAI

from api.dtos.chat_dtos import UserPrompt

client = AsyncAzureOpenAI(
    api_key="Fl2MFnbWqc0tnY9rK53c3KnbDbEZCs8PjrVZ3fl4krVtV3A3vPEZJQQJ99AKACHYHv6XJ3w3AAAAACOG0sUE",
    api_version="2024-08-01-preview",
    azure_endpoint="https://moha3-m3uad3g1-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview",
)


async def make_chat(prompt: UserPrompt, client: AsyncAzureOpenAI = client):
    response = await client.chat.completions.create(
        model="gpt-4",  # model = "deployment_name".
        messages=[
            {
                "role": "system",
                "content": "Assistant is a large language model trained by OpenAI.",
            },
            {"role": "user", "content": prompt.prompt},
        ],
        temperature=0,
    )

    print("the prompt given: ", prompt)
    print("------------------------------")
    print(response.choices[0].message.content)

    return response
