from typing import List
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AzureOpenAI
import config

app = FastAPI()

# Initialize AzureOpenAI client
client = AzureOpenAI(
    azure_endpoint=config.azure_openai_endpoint,
    api_key=config.azure_openai_key_key,
    api_version=config.azure_api_version,
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


def stream_response(messages: List[Message]):
    response = client.chat.completions.create(
        model=config.azure_openai_deployment_name,
        messages=[message.model_dump() for message in messages],
        temperature=0,
        stream=True
    )

    for chunk in response:
        if chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                yield delta.content.encode('utf-8')


@app.post("/stream-chat/")
async def stream_chat(chat_request: ChatRequest):
    return StreamingResponse(stream_response(chat_request.messages))

# Run the app with: uvicorn this_file_name:app --reload

# Test the app with:
# ❯ curl -X 'POST' \
#           'http://127.0.0.1:8000/stream-chat/' \
#           -H 'accept: application/json' \
#              -H 'Content-Type: application/json' \
#                 -d '{
# "messages": [
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "write 20 sentence about cow"}
# ]
# }'