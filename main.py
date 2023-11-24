from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from pydantic import BaseModel
from typing import List
import logging

from core.azure_functions import AzureOpenAIFunctions
import config
import functions.argocd as argocd
import functions.websearch as websearch
import functions.weather as weather

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.propagate = True


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


# Initialize the gpt with the functions we want to use
gpt = AzureOpenAIFunctions(
    azure_openai_endpoint=config.azure_openai_endpoint,
    azure_openai_key_key=config.azure_openai_key_key,
    azure_api_version=config.azure_api_version,
    model=config.azure_openai_deployment_name,
    functions=[
        argocd.get_available_applications,
        argocd.get_application_status,
        websearch.web_search,
        websearch.scrape_webpage,
        weather.get_weather,
    ]
)

system_prompt = """You are an AI assistant with access to websearch, Argocd, and weather functions.

The websearch function empowers you for real-time web search and information retrieval, particularly for current and 
relevant data from the internet in response to user queries, especially when such information is beyond your training 
data or when up-to-date information is essential. Always include the source URL for information fetched from the web.

The Argocd function facilitates real-time interaction with the Argocd instance, enabling you to fetch information about 
applications deployed in the cluster. 

The weather function provides real-time capabilities to offer current weather updates. 

All your responses should be in a human-readable format.
"""


@app.post("/assistant/{conversation_id}")
async def endpoint(conversation_id: str, conversation: Conversation):
    system_message = Message(role='system', content=system_prompt)
    conversation.conversation.insert(0, system_message)
    conversation_dict = [message.model_dump() for message in conversation.conversation]
    logger.debug(f"Conversation: {conversation_dict}")
    response = gpt.ask(conversation_dict)
    logger.debug(f"Reply: {response.choices[0].message.content}")
    return {"id": conversation_id, "reply": response.choices[0].message.content}


if __name__ == "__main__":
    response = gpt.ask([{'role': 'user', 'content': 'Summarize the article in 2 sentences https://www.bbc.com/news/technology-67514068'}])
    print(response.choices[0].message.content)

# Questions:
# -- Is Sam Altman fired from OpenAI?
# -- How many argocd applications are available?
# -- How many argocd applications are available? And what are their status?
# -- Who won ICC world cup 2023?
# -- What is the weather in Berlin today?
# -- Is there any possibility of rain in Berlin today?
# -- Summarize the article in 5 sentences https://www.bbc.com/news/technology-67514068
