import logging
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import json
from core.azure_functions import AzureOpenAIFunctions
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchManager:
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

    def generate_google_search_query(self, search_query):
        """
        Generates an optimized Google Search query using GPT-4-turbo.
        """
        messages = [
            {"role": "system",
             "content": "You are a Google Search Expert. You task is to convert unstructured user inputs to optimized "
                        "Google search queries. For example, USER INPUT: 'What is the current weather in Berlin?' "
                        "OPTIMIZED Google Search Query: 'current weather Berlin'"},
            {"role": "user",
             "content": f"Convert the following user query into a optimized Google Search query: {search_query}"}
        ]
        try:
            response = self.gpt.ask(messages)
            if response.choices:
                optimized_query = response.choices[0].message
                if hasattr(optimized_query, "content"):
                    return optimized_query.content.strip()
        except Exception as e:
            logger.error(f"Error in generating Google Search query: {e}")
            raise

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

    def scrape_website(self, url):
        """
        Scrapes the content of the given URL.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                page_content = response.content
                soup = BeautifulSoup(page_content, "html.parser")
                paragraphs = soup.find_all("p")
                scraped_data = [paragraph.get_text() for paragraph in paragraphs]
                formatted_data = "\n".join(scraped_data)
                return url, formatted_data
        except Exception as e:
            return url, f"Failed to retrieve the webpage: {e}"

    def search_query(self, query):
        """
        The entrypoint for performing a web search and scraping the content.
        """
        try:
            optimized_query = self.generate_google_search_query(query)
            # print(f"Optimized Google Search Query: {optimized_query}")
            urls = self.google_search(optimized_query)
            scraped_data = [self.scrape_website(url) for url in urls]
            return json.dumps(scraped_data, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})


# Usage Example
if __name__ == "__main__":
    web = WebSearchManager()
    result = web.search_query("Who won ICC Cricket World Cup 2023?")
    if result is not None:
        print(result)
    else:
        logger.error("Failed to process the search query.")
