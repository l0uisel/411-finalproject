from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from movie_collection.utils.logger import configure_logger
from movie_collection.utils.omdb_utils import get_omdb_data
from movie_collection.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)

# SQLAlchemy setup
DB_PATH = os.getenv("DB_PATH", "sqlite:///app/db/movie_catalog.db")  # Default to SQLite if no environment variable
ENCODING = os.getenv("ENCODING", "utf-8")
engine = create_engine(DB_PATH, echo=False)  # Set echo=True for SQL logging during development
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

class WatchlistModel:
    """
    A class to manage a watchlist of movies.

    Attributes:
        current_movie_number (int): current movie being watched.
        watchlist (List[Movie]): list of movies in the watchlist.
    """

    def __init__(self):
        """
        Initializes the WatchlistModel with an empty watchlist and the current movie set to 1.
        """
        self.current_movie_number = 1
        self.watchlist: List[Movie] = []

    ##################################################
    # Movie Management Functions
    ##################################################

    def add_movie_to_watchlist(self, movie: Movie) -> None:
        """
        Adds a movie to the watchlist.

        Args:
            movie (Movie): movie to add.

        Raises:
            TypeError: If the movie is not a valid Movie instance.
            ValueError: If a movie with the same 'id' already exists.
        """
        logger.info("Adding new movie to watchlist")
        if not isinstance(movie, Movie):
            logger.error("Invalid movie object")
            raise TypeError("Invalid movie object")

        if movie.id in [movie_in_watchlist.id for movie_in_watchlist in self.watchlist]:
            logger.error("Movie with ID %d already exists", movie.id)
            raise ValueError(f"Movie with ID {movie.id} already exists in the watchlist")

        self.watchlist.append(movie)

    def remove_movie_by_id(self, movie_id: int) -> None:
        """
        Removes a movie from the watchlist by its ID.

        Args:
            movie_id (int): ID of the movie to remove.

        Raises:
            ValueError: If the watchlist is empty or the movie ID is invalid.
        """
        logger.info("Removing movie with ID %d", movie_id)
        self.check_if_empty()
        self.watchlist = [movie for movie in self.watchlist if movie.id != movie_id]

    def clear_watchlist(self) -> None:
        """
        Clears all movies from the watchlist.
        """
        logger.info("Clearing watchlist")
        self.watchlist.clear()

    ##################################################
    # Watchlist Retrieval Functions
    ##################################################

    def get_all_movies(self) -> List[Movie]:
        """
        Returns all movies in the watchlist.
        """
        self.check_if_empty()
        logger.info("Getting all movies in the watchlist")
        return self.watchlist

    def get_movie_by_id(self, movie_id: int) -> Movie:
        """
        Retrieves a movie by its ID.

        Args:
            movie_id (int): The ID of the movie.

        Raises:
            ValueError: If the movie is not found.
        """
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        logger.info("Getting movie with id %d from watchlist", movie_id)
        return next((movie for movie in self.watchlist if movie.id == movie_id), None)

    def get_current_movie(self) -> Movie:
        """
        Returns the current movie being watched.
        """
        self.check_if_empty()
        return self.watchlist[self.current_movie_number - 1]

    ##################################################
    # Watchlist Ordering Functions
    ##################################################

    def move_movie_to_beginning(self, movie_id: int) -> None:
        """
        Moves a movie to the beginning of the watchlist.
        """
        self.check_if_empty()
        movie = self.get_movie_by_id(movie_id)
        self.watchlist.remove(movie)
        self.watchlist.insert(0, movie)

    def move_movie_to_end(self, movie_id: int) -> None:
        """
        Moves a movie to the end of the watchlist.
        """
        self.check_if_empty()
        movie = self.get_movie_by_id(movie_id)
        self.watchlist.remove(movie)
        self.watchlist.append(movie)

    def check_if_empty(self) -> None:
        """
        Checks if the watchlist is empty and raises an error if it is.
        """
        if not self.watchlist:
            logger.error("Watchlist is empty")
            raise ValueError("Watchlist is empty")

# Ensure the logger is configured
logging.basicConfig(level=logging.INFO)
