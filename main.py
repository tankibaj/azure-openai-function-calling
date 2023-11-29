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
import functions.web_browsing as browser
import functions.weather as weather

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.propagate = True


# -- The message schema for the assistant
class Message(BaseModel):
    role: str
    content: str


# -- The conversation schema for the assistant
class Conversation(BaseModel):
    conversation: List[Message]


# -- Initialize the FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Exception handler for the FastAPI app
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc):
    return PlainTextResponse(str(exc), status_code=400)


system_prompt = """You are an AI assistant with access to websearch, Argocd, and weather functions.

The websearch function empowers you for real-time web search and information retrieval, particularly for current and 
relevant data from the internet in response to user queries, especially when such information is beyond your training 
data or when up-to-date information is essential. Always include the source URL for information fetched from the web.

The Argocd function facilitates real-time interaction with the Argocd instance, enabling you to fetch information about 
applications deployed in the cluster. 

The weather function provides real-time capabilities to offer current weather updates. 

All your responses should be in a human-readable format.
"""

# Initialize the assistant (GPT Model) with the functions
assistant = AzureOpenAIFunctions(
    azure_openai_endpoint=config.azure_openai_endpoint,
    azure_openai_key_key=config.azure_openai_key_key,
    azure_api_version=config.azure_api_version,
    model=config.azure_openai_deployment_name,
    functions=[
        argocd.get_available_applications,
        argocd.get_application_status,
        weather.get_weather,
        browser.text_search,
        browser.news_search,
        browser.images_search,
        browser.videos_search,
        browser.maps_search,
        browser.webpage_scraper
    ]
)


# -- FastAPI endpoints
@app.post("/assistant/{conversation_id}")
async def endpoint(conversation_id: str, conversation: Conversation):
    system_message = Message(role='system', content=system_prompt)
    conversation.conversation.insert(0, system_message)
    conversation_dict = [message.model_dump() for message in conversation.conversation]
    logger.debug(f"Conversation: {conversation_dict}")
    response = assistant.ask(conversation_dict)
    logger.debug(f"Reply: {response.choices[0].message.content}")
    return {"id": conversation_id, "reply": response.choices[0].message.content}


# -- Test the assistant. This is not part of the FastAPI app, only for demonstration purposes.
if __name__ == "__main__":
    prompt = "Is Sam Altman fired from OpenAI?"
    response = assistant.ask([{'role': 'user', 'content': f'{prompt}'}])
    # ANSI escape sequences for colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'  # Resets the color to default
    print(f"{RED}\nQuery: {prompt} {ENDC}\n")
    print(f"{GREEN}Reply: {response.choices[0].message.content}{ENDC}")

# Features:
# -- Web search
# -- Video search
# -- Location search
# -- Image search
# -- Summarize article from URL
# -- Weather information
# -- Integration with ArgoCD application through rest API.

# === Questions ===
# ---- General search to recent events ----
# -- Is Sam Altman fired from OpenAI?
# -- What happened to HSBC bank in UK?
# -- What happened to WeWork?

# ---- About a person ----
# -- Who is Frank Gotthard?

# ---- Video search ----
# -- Provide video tutorial for Excel pivot table.
# -- Provide video tutorial for Python pandas.
# -- Show me a video about how to make a cake.

# ---- Location search ----
# -- Suggestions for the top 3 Italian restaurant in Munich.

# ---- Image search ----
# -- Provide puppies images.
# -- Provide 10 images of cats.
# -- Show me pictures of the Eiffel Tower.
# -- Show me pictures of the Eiffel Tower at night.

# ---- Weather ----
# -- What is the weather in Berlin today?
# -- Is there any possibility of rain in Berlin today?

# ---- Summarize from URL ----
# -- Summarize the article in 3 sentences https://www.bbc.com/news/world-us-canada-67482231

# ---- External application ----
# -- How many argocd applications are available?
# -- How many argocd applications are available? And what are their status?
