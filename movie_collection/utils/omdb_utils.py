import logging
import requests
import os

from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

API_KEY = os.getenv("API_KEY")


def get_omdb_data(title: str) -> dict:
    """
    Fetches the rating of a movie from the OMDB API.

    Returns:
        data: The data of the movie.

    Raises:
        RuntimeError: If the request to omdbapi.com fails or returns an invalid response.
        ValueError: If the response from omdbapi.com is not a valid data.
    """
    url=f"https://www.omdbapi.com/?t={title}&apikey={API_KEY}"

    try:
        # Log the request to omdbapi.com
        logger.info("Fetching data from %s", url)
        response = requests.get(url, timeout=5)
        # Check if the request was successful
        response.raise_for_status()
        data = response.json()

        if data["Response"] == "False":
            logger.error("Invalid response from omdbapi.com: %s", data["Error"])
            raise ValueError(f"Invalid response from omdbapi.com: {data['Error']}")

        logger.info(f"Received data: {data}")
        return data

    except requests.exceptions.Timeout:
        logger.error("Request to omdbapi.com timed out.")
        raise RuntimeError("Request to omdbapi.com timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to omdbapi.com failed: %s", e)
        raise RuntimeError("Request to omdbapi.com failed: %s" % e)

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error from omdbapi.com: %s", e)
        raise RuntimeError("HTTP error from omdbapi.com: %s" % e)
