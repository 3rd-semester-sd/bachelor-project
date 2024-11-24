import pprint
from openai import AsyncAzureOpenAI
import asyncio

client = AsyncAzureOpenAI(
    api_key="Fl2MFnbWqc0tnY9rK53c3KnbDbEZCs8PjrVZ3fl4krVtV3A3vPEZJQQJ99AKACHYHv6XJ3w3AAAAACOG0sUE",
    api_version="2024-08-01-preview",
    azure_endpoint="https://moha3-m3uad3g1-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview",
)


async def make_chat():
    prompt = "Give me 3 restaurants from copenhagen that is in the center. WHo are also"
    response = await client.chat.completions.create(
        model="gpt-4",  # model = "deployment_name".
        messages=[
            {
                "role": "system",
                "content": "Assistant is a large language model trained by OpenAI.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    print("the prompt given", prompt)
    print("------------------------------")
    print(response.choices[0].message.content)

    return response


asyncio.run(make_chat())
