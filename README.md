# Enhanced GPT Web Search Capabilities

## Overview
This project extends the capabilities of an Azure OpenAI GPT model to include advanced web search functionalities. It allows the GPT model to fetch and return relevant information from the internet, including general web content, videos, locations, images, and article summaries. Additionally, it provides weather information and integrates with ArgoCD applications through REST API.

## Key Features
- **Web Search**: Empowers the GPT model to perform general web searches and return results.
- **Video Search**: Fetches video content relevant to the query.
- **Location Search**: Finds geographical locations related to the search terms.
- **Image Search**: Retrieves images based on the search criteria.
- **Summarize Articles**: Processes URLs to extract and summarize article content.
- **Weather Information**: Gathers and provides weather data.
- **ArgoCD Integration**: Manages and interacts with ArgoCD applications via REST API.


## Usage

### Running Locally with Uvicorn
- Run the application using Uvicorn:
  ```bash
  uvicorn main:app --reload
  ```

### Building and Running with Docker
1. **Build the Docker Image**
    - Navigate to the root directory of the project.
    - Build the Docker image using the provided `Dockerfile`.
      ```bash
      docker build -t gpt-web-search-app .
      ```

2. **Run the Docker Container**
    - Once the image is built, run the container.
      ```bash
      docker run -p 8000:8000 gpt-web-search-app
      ```

    - This command runs the Docker container and maps the container's port 8000 to the local port 8000. Adjust the port mapping as necessary based on your configuration.

3. **Accessing the Application**
    - With the Docker container running, the application should be accessible at `http://localhost:8000`.

### Accessing FastAPI Documentation
- **Swagger UI**: Navigate to `http://localhost:8000/docs`. This interactive UI allows you to execute API calls directly from the browser.
- **ReDoc**: For an alternative documentation format, visit `http://localhost:8000/redoc`.



## Sample Questions to Ask the Model

### General Search to Recent Events
- Is Sam Altman fired from OpenAI?
- What happened to HSBC bank in the UK?
- What happened to WeWork?**
- What happened to the stock market today?

### About a Person
- Who is Frank Gotthard?

### Video Search
- Provide a video tutorial for Excel pivot tables.
- Show me a video about how to make a cake.

### Location Search
- Suggestions for the top 3 Italian restaurants in Munich.

### Image Search
- Provide puppies images.
- Provide 10 images of cats.
- Show me pictures of the Eiffel Tower.
- Show me pictures of the Eiffel Tower at night.

### Weather
- What is the weather in Berlin today?
- Is there any possibility of rain in Berlin today?

### Summarize from URL
- Summarize the article in 3 sentences: https://www.bbc.com/news/world-us-canada-67482231

### External Application (ArgoCD)
- How many ArgoCD applications are available?
- What are the statuses of the ArgoCD applications?





## Contributing
We welcome contributions to the project. Please follow the standard fork-and-pull request workflow.