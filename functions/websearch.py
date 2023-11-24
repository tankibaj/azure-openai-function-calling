from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from core.azure_functions import AzureOpenAIFunctions
import config
import json

gpt = AzureOpenAIFunctions(
    azure_openai_endpoint=config.azure_openai_endpoint,
    azure_openai_key_key=config.azure_openai_key_key,
    azure_api_version=config.azure_api_version,
    model=config.azure_openai_deployment_name,
)


def generate_google_search_query(search_query):
    """
    Uses GPT-4-turbo to convert user input into an optimized Google Search query.
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
        response = gpt.ask(messages)
        if response.choices:
            optimized_query = response.choices[0].message
            if hasattr(optimized_query, "content"):
                return optimized_query.content.strip()
    except Exception as e:
        return f"Error in generating Google Search query: {e}"


def google_search(query, num_results=3, location="United States"):
    """
    Uses SerpAPI to perform a Google Search.
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


def scrape_website(url):
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


if __name__ == "__main__":
    # search_query = "What is the current weather in Berlin?"
    # optimized_query = generate_google_search_query(search_query)
    # print(f"User Input: {search_query}")
    # print(f"Optimized Google Search Query: {optimized_query}")
    # urls = google_search(optimized_query)
    urls = google_search("Weather Today Berlin")
    # print(json.dumps(urls, indent=2))
    scraped_data = [scrape_website(url) for url in urls]
    # print(json.dumps(scraped_data, indent=2))

