from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from movie_collection.utils.logger import configure_logger
from movie_collection.utils.rating_utils import get_rating
from movie_collection.utils.sql_utils import get_db_connection


@dataclass
class Movie:
    id: int
    #actors or director: str 
    title: str
    genre: str
    year: int
    duration: int  # in seconds
    

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError(f"Duration must be greater than 0, got {self.duration}")
        if self.year <= 1900:
            raise ValueError(f"Year must be greater than 1900, got {self.year}")


def create_movie(director: str, title: str, genre: str, year: int, duration: int) -> None:
    """
    Creates a new movie in the movie table.

    Args:
        director (str): The director of the movie
        title (str): The movie's name.
        genre (str): The genre of the movie.
        year (int): The year the movie was released.
        duration (int): The duration of the movie in seconds.

    Raises:
        ValueError: If year or duration are invalid.
        sqlite3.IntegrityError: If a song with the same compound key (director, title, year) already exists. #confirm using director
        sqlite3.Error: For any other database errors.
    """
    # Validate the required fields
    if not isinstance(year, int) or year < 1900:
        raise ValueError(f"Invalid year provided: {year} (must be an integer greater than or equal to 1900).")
    if not isinstance(duration, int) or duration <= 0:
        raise ValueError(f"Invalid song duration: {duration} (must be a positive integer).")

    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO songs (director, title, genre, year, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (director, title, genre, year, duration))
            conn.commit()

            logger.info("Movie created successfully: %s - %s (%d)", director, title, year) #maybe add back director

    except sqlite3.IntegrityError as e:
        logger.error("Song with director '%s', title '%s', and year %d already exists.", director, title, year)
        raise ValueError(f"Song with artist '{director}', title '{title}', and year {year} already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating song: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")



def delete_movie(movie_id: int) -> None:
    """
    Soft deletes a movie from the catalog by marking it as deleted.

    Args:
        movie_id (int): The ID of the movie to delete.

    Raises:
        ValueError: If the movie with the given ID does not exist or is already marked as deleted.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the song exists and if it's already deleted
            cursor.execute("SELECT deleted FROM movies WHERE id = ?", (movie_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("movie with ID %s has already been deleted", movie_id)
                    raise ValueError(f"Movie with ID {movie_id} has already been deleted")
            except TypeError:
                logger.info("Movie with ID %s not found", movie_id)
                raise ValueError(f"Movie with ID {movie_id} not found")

            # Perform the soft delete by setting 'deleted' to TRUE
            cursor.execute("UPDATE movies SET deleted = TRUE WHERE id = ?", (movie_id,))
            conn.commit()

            logger.info("movie with ID %s marked as deleted.", movie_id)

    except sqlite3.Error as e:
        logger.error("Database error while deleting movie: %s", str(e))
        raise e



def get_movie_by_id(movie_id: int) -> Movie:
    """
    Retrieves a movie from the catalog by its movie ID.

    Args:
        movie_id (int): The ID of the movie to retrieve.

    Returns:
        Movie: The Movie object corresponding to the movie_id.

    Raises:
        ValueError: If the movie is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve movie with ID %s", movie_id)
            cursor.execute("""
                SELECT id, director, title, genre, year, duration, deleted
                FROM songs
                WHERE id = ?
            """, (movie_id,))
            row = cursor.fetchone()

            if row:
                if row[6]:  # deleted flag
                    logger.info("Movie with ID %s has been deleted", movie_id)
                    raise ValueError(f"Song with ID {movie_id} has been deleted")
                logger.info("Song with ID %s found", movie_id)
                return Movie(id=row[0], director=row[1], title=row[2], genre=row[3], year=row[4], duration=row[5])
            else:
                logger.info("Movie with ID %s not found", movie_id)
                raise ValueError(f"Movie with ID {movie_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving movie by ID %s: %s", movie_id, str(e))
        raise e
    


def get_movie_by_compound_key(director: str, title: str, year: int) -> Song:
    """
    Retrieves a song from the catalog by its compound key (director, title, year).

    Args:
        director (str): The director of the movie.
        title (str): The title of the movie.
        year (int): The year of the movie.

    Returns:
        Movie: The Movie object corresponding to the compound key.

    Raises:
        ValueError: If the movie is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve movie with director '%s', title '%s', and year %d", director, title, year)
            cursor.execute("""
                SELECT id, director, title, genre, year, duration, deleted
                FROM songs
                WHERE director = ? AND title = ? AND year = ?
            """, (director, title, year))
            row = cursor.fetchone()

            if row:
                if row[6]:  # deleted flag
                    logger.info("Meal with director '%s', title '%s', and year %d has been deleted", director, title, year)
                    raise ValueError(f"Movie with director '{director}', title '{title}', and year {year} has been deleted")
                logger.info("Movie with director '%s', title '%s', and year %d found", artist, title, year)
                return Meal(id=row[0], director=row[1], title=row[2], genre=row[3], year=row[4], duration=row[5])
            else:
                logger.info("Movie with director '%s', title '%s', and year %d not found", director, title, year)
                raise ValueError(f"Song with director '{director}', title '{title}', and year {year} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving movie by compound key (director '%s', title '%s', year %d): %s", director, title, year, str(e))
        raise e



def get_all_movies(sort_by_play_count: bool = False) -> list[dict]: #do i need to chnage sort by play count?
    """
    Retrieves all movies that are not marked as deleted from the catalog.

    Args:
        sort_by_play_count (bool): If True, sort the movies by play count in descending order.

    Returns:
        list[dict]: A list of dictionaries representing all non-deleted movies with play_count.

    Logs:
        Warning: If the catalog is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-deleted movies from the catalog")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT id, director, title, genre, year, duration, play_count
                FROM movies
                WHERE deleted = FALSE
            """
            if sort_by_play_count:
                query += " ORDER BY play_count DESC"

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The movie catalog is empty.")
                return []

            songs = [
                {
                    "id": row[0],
                    "director": row[1],
                    "title": row[2],
                    "genre": row[3],
                    "year": row[4],
                    "duration": row[5],
                    "play_count": row[6],
                }
                for row in rows
            ]
            logger.info("Retrieved %d movies from the catalog", len(Movie))
            return movie

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all songs: %s", str(e))
        raise e
