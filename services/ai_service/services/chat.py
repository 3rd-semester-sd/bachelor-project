from openai import AsyncAzureOpenAI

from api.dtos.chat_dtos import UserPrompt
from services.client import client


async def make_chat(prompt: UserPrompt, client: AsyncAzureOpenAI = client):
    print("prompt len", len(prompt.prompt))
    response = await client.chat.completions.create(
        model="gpt-35-turbo",  # model = "deployment_name".
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
