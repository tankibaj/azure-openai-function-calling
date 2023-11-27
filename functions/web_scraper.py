import json
import logging

import requests
from bs4 import BeautifulSoup

# Configure logging
logging = logging.getLogger(__name__)


class WebContentScraper:
    def __init__(self, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"):
        self.headers = {"User-Agent": user_agent}

    def _fetch_page_content(self, url):
        """Fetches the content of a web page from a given URL.

        Parameters:
        - url (str): The URL of the web page to be fetched.

        Returns:
        - bytes: The content of the web page in bytes if the request is successful; otherwise, None.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raises HTTPError for bad requests
            return response.content
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return None
        except Exception as err:
            logging.error(f"Error occurred: {err}")
            return None

    def _parse_web_content(self, content):
        """Parses HTML content and extracts text from it.

        Parameters:
        - content (bytes or str): The HTML content to be parsed. It can be in bytes or
          a string format. If in bytes, BeautifulSoup will handle the decoding.

        Returns:
        - str: A single string containing all the extracted text from paragraph elements,
          separated by newlines. If parsing fails, returns None.
        """
        try:
            soup = BeautifulSoup(content, "html.parser")
            paragraphs = soup.find_all("p")
            return "\n".join(paragraph.get_text() for paragraph in paragraphs)
        except Exception as e:
            logging.error(f"Failed to parse the content: {e}")
            return None

    def scrape_website(self, url):
        """Scrapes the content from a given website URL.

        Parameters:
        - url (str): The URL of the website to be scraped.

        Returns:
        - dict: A dictionary with two keys:
            - 'url': The URL of the website.
            - 'content': The scraped and parsed content from the website, if successful.
            - 'error': An error message, if the scraping process failed at any stage.
        """
        logging.debug(f"Scraping URL: {url}")
        page_content = self._fetch_page_content(url)
        if page_content:
            parsed_content = self._parse_web_content(page_content)
            if parsed_content:
                return {"url": url, "content": parsed_content}
            else:
                return {"url": url, "error": "Failed to parse content"}
        return {"url": url, "error": "Failed to fetch page content"}

    def scrape_multiple_websites(self, urls):
        """Scrapes the content from multiple websites.

        Parameters:
        - urls (list of str): A list of URLs of the websites to be scraped.

        Returns:
        - str: A JSON-formatted string. Each element in the JSON represents the result
          of scraping a single URL, containing either the scraped content or an error message.
        """
        try:
            return json.dumps([self.scrape_website(url) for url in urls], indent=2)
        except Exception as e:
            logging.error(f"Error during scraping multiple websites: {e}")
            return json.dumps({"error": str(e)})
