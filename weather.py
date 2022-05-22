# weather.py

import argparse
import json
import style
import sys # exit program without traceback
from configparser import ConfigParser
from urllib import parse, request
from urllib import error, parse, request #adds error to imports
from pprint import pp #makes print prettier

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather" #base URL that all API calls will share as a constant
PADDING = 20

def change_color(color):
    print(color, end="")

def _get_api_key():
    """Fetch the API key from your configuration file.

    Expects a configuration file named "secrets.ini" with structure:

        [openweather]
        api_key=<YOUR-OPENWEATHER-API-KEY>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def read_user_cli_args():
    """Handles the CLI user interactions.

    Returns:
        argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )

    # set up parser to take in 2 arguments

    parser.add_argument( #takes in a city argument which allows white space inbetween
        "city", nargs="+", type=str, help="enter the city name" #-h shows helpful text for this argument
    )
    parser.add_argument( #takes in a optional Bool argument (-i / --imperial). if inputted, store_true is True and False if not inputted
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature in imperial units",  #-h shows helpful text for this argument
    )

    return parser.parse_args()


# returns a URL that you can use to make a valid API call to a specific endpoint of the weather API provided by OpenWeather
def build_weather_query(city_input, imperial=False):
    """Builds the URL for an API request to OpenWeather's weather API.

    Args:
        city_input (List[str]): Name of a city as collected by argparse
        imperial (bool): Whether or not to use imperial units for temperature

    Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)  #puts a space between eaach city name
    url_encoded_city_name = parse.quote_plus(city_name)  #makes it url freindly
    units = "imperial" if imperial else "metric"
    url = (  #creates complete url with f-string
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url

# ...

def get_weather_data(query_url):
    """Makes an API request to a URL and returns the data as a Python object.

    Args:
        query_url (str): URL formatted for OpenWeather's city name endpoint

    Returns:
        dict: Weather information for a specific city
    """
    try:
        response = request.urlopen(query_url) #makes HTTP GET request
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read() #extracts data
    
    try:
        return json.loads(data) #returns python object as json
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_weather_info(weather_data, imperial=False):
    """Prints formatted weather information about a city.

    Args:
        weather_data (dict): API response from OpenWeather by city name
        imperial (bool): Whether or not to use imperial units for temperature

    More information at https://openweathermap.org/current#name
    """
    city = weather_data["name"]
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]

    print(f"{city:^{PADDING}}", end="")
    print(
        f"\t{weather_description.capitalize():^{PADDING}}",
        end=" ",
    )
    print(f"({temperature}°{'F' if imperial else 'C'})")


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)