from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from pydantic import BaseModel
from typing import List
import logging

from core.agent import FunctionsAgent
import functions.argocd as argocd
import config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    conversation: List[Message]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc):
    return PlainTextResponse(str(exc), status_code=400)


agent = FunctionsAgent(
    azure_openai_endpoint=config.azure_openai_endpoint,
    azure_openai_key_key=config.azure_openai_key_key,
    azure_api_version=config.azure_api_version,
    model=config.azure_openai_deployment_name,
    functions=[
        argocd.get_available_applications,
        argocd.get_application_status
    ]
)

system_prompt = """You are a DevOps assistant developed by Naim. 

You have exceptional capabilities and I can rely on you to execute various functions to manage our software deployments efficiently. 

By leveraging the power of the OpenAI GPT-4 API's function calling feature, you can seamlessly interact with our git repositories (e.g., gitops repository) and Kubernetes cluster. 

Your expertise is invaluable in handling our applications' lifecycle effectively. 

Please provide short answers to user queries unless asked to answer in detail.

All responses to be in Human readable format.
"""


@app.post("/assistant/{conversation_id}")
async def endpoint(conversation_id: str, conversation: Conversation):
    system_message = Message(role='system', content=system_prompt)
    conversation.conversation.insert(0, system_message)
    conversation_dict = [message.model_dump() for message in conversation.conversation]
    logger.debug(f"Conversation: {conversation_dict}")
    response = agent.ask(conversation_dict)
    logger.debug(f"Reply: {response.choices[0].message.content}")
    return {"id": conversation_id, "reply": response.choices[0].message.content}


if __name__ == "__main__":
    response = agent.ask([{'role': 'user', 'content': 'How many argocd applications are available?'}])
    print(response.choices[0].message.content)
