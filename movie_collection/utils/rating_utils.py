import logging
import requests
import os

from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

API_KEY = os.getenv("API_KEY")


def get_rating(imdb_id: str) -> float:
    """
    Fetches the rating of a movie from the OMDB API.

    Returns:
        float: The rating of the movie.

    Raises:
        RuntimeError: If the request to omdbapi.com fails or returns an invalid response.
        ValueError: If the response from omdbapi.com is not a valid float.
    """
    url=f"https://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}"

    try:
        # Log the request to omdbapi.com
        logger.info("Fetching data from %s", url)

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        rating = response.json()
        rating = rating["imdbRating"]

        try:
            rating = float(rating)
        except ValueError:
            raise ValueError("Invalid response from omdbapi.com: %s" % rating)

        logger.info("Received rating:  %.3f", rating)
        return rating

    except requests.exceptions.Timeout:
        logger.error("Request to omdbapi.com timed out.")
        raise RuntimeError("Request to omdbapi.com timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to omdbapi.com failed: %s", e)
        raise RuntimeError("Request to omdbapi.com failed: %s" % e)

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error from omdbapi.com: %s", e)
        raise RuntimeError("HTTP error from omdbapi.com: %s" % e)
