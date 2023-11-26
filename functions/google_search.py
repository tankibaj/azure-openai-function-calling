import logging
from serpapi import GoogleSearch
from core.azure_functions import AzureOpenAIFunctions
import config

# Configure logging
logger = logging.getLogger(__name__)


class GoogleSearchManager:
    """
    A class to perform web searches and scrape web content.
    """

    def __init__(self):
        self.gpt = AzureOpenAIFunctions(
            azure_openai_endpoint=config.azure_openai_endpoint,
            azure_openai_key_key=config.azure_openai_key_key,
            azure_api_version=config.azure_api_version,
            model=config.azure_openai_deployment_name,
        )

    # def generate_google_search_query(self, search_query):
    #     """
    #     Generates an optimized Google Search query using GPT-4-turbo.
    #     """
    #     messages = [
    #         {"role": "system",
    #          "content": "You are a Google Search Expert. You task is to convert unstructured user inputs to optimized "
    #                     "Google search queries. For example, USER INPUT: 'What is the current weather in Berlin?' "
    #                     "OPTIMIZED Google Search Query: 'current weather Berlin'"},
    #         {"role": "user",
    #          "content": f"Convert the following user query into a optimized Google Search query: {search_query}"}
    #     ]
    #     try:
    #         response = self.gpt.ask(messages)
    #         if response.choices:
    #             optimized_query = response.choices[0].message
    #             if hasattr(optimized_query, "content"):
    #                 return optimized_query.content.strip()
    #     except Exception as e:
    #         logger.error(f"Error in generating Google Search query: {e}")
    #         raise

    def google_search(self, query, num_results=3, location="United States"):
        """
        Performs a Google Search and returns a list of URLs.
        """
        params = {
            "api_key": config.serpapi_key,
            "engine": "google",
            "q": query,
            "num": str(num_results),
            "tbm": "nws",  # Search type: news, images, videos, shopping, books, apps
            "location": location,
            "hl": "en",  # language
            "gl": "us",  # country code to search from (e.g. United States = us, Germany = de)
            "google_domain": "google.com",  # google domain to search from
            "output": "json",
            "safe": "active",
        }
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            news_results = results.get("news_results", [])
            urls = [result["link"] for result in news_results]
            return urls
        except Exception as e:
            return f"Error in performing Google Search: {e}"


# Usage Example
if __name__ == "__main__":
    web = GoogleSearchManager()
    result = web.google_search("Is Sam Altman fired from OpenAI?")
    if result is not None:
        print(result)
    else:
        logger.error("Failed to process the search query.")
