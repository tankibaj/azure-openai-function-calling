import os
from dotenv import load_dotenv

load_dotenv()

openai_api_type = os.getenv('OPENAI_API_TYPE', 'azure')
openai_api_version = os.getenv('OPENAI_API_VERSION', '2023-07-01-preview')
openai_api_base = os.getenv('OPENAI_API_BASE')  # The Azure OpenAI resource's endpoint value.
openai_api_key = os.getenv('OPENAI_API_KEY', None)
openai_engine = os.getenv('OPENAI_ENGINE')  # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model
argocd_url = os.getenv('ARGOCD_URL')
argocd_api_key = os.getenv("ARGOCD_API_KEY", None)
