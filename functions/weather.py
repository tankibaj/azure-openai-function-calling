import json
import requests
import config


def get_weather(city, api_key=config.openweathermap_key):
    """Fetch the current weather for a given city using OpenWeatherMap API. The output should be in Markdown format.

    This function enables real-time weather information retrieval for GPT models. It fetches current weather data
    from the internet in response to user queries, enhancing GPT's knowledge base and reducing reliance on
    pre-trained information and reducing hallucinations.

    :param city: The city name to fetch weather information for.
    :return: A JSON-formatted string containing the weather information. In case of an error, it returns a JSON-formatted string with an error message.
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return json.dumps({"error": f"Error occurred while fetching weather data: {e}"})


if __name__ == "__main__":
    city_name = 'Berlin'  # Replace with your desired city
    weather_data = get_weather(city_name)

    # print(json.dumps(weather_data, indent=2))
    print(weather_data)
