import json
from functions.websearch_manager import WebSearchManager


def web_search(query):
    """Search the web for a specific query.

    This function enables real-time web search and information retrieval for GPT models. It fetches current,
    relevant data from the internet in response to user queries, enhancing GPT's knowledge base and reducing reliance
    on pre-trained information and reducing hallucinations.

    :param query: The user query to fetch information from the web.
    :return: A JSON-formatted string containing the search results. In case of an error, it returns a JSON-formatted string with an error message.
    """
    try:
        web = WebSearchManager()
        result = web.search_query(query)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


def scrape_webpage(url):
    """Scrape a webpage for its text content.

    This function enables web scraping for GPT models. It fetches the text content of a webpage and returns it to the
    model. Use this function if user queries include a URL.

    :param url: The URL of the webpage to scrape.
    :return: A JSON-formatted string containing the scraped text. In case of an error, it returns a JSON-formatted string with an error message.
    """
    try:
        web = WebSearchManager()
        result = web.scrape_website(url)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


# if __name__ == "__main__":
#     print(scrape_webpage("https://www.bbc.com/news/technology-67514068"))
