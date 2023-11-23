import os
from dotenv import load_dotenv

load_dotenv()

azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
azure_openai_key_key = os.getenv('AZURE_OPENAI_KEY')
azure_api_version = os.getenv('AZURE_API_VERSION', '2023-07-01-preview')
azure_openai_deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
argocd_url = os.getenv('ARGOCD_URL')
argocd_api_key = os.getenv("ARGOCD_API_KEY", None)
