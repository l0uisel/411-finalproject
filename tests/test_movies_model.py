from contextlib import contextmanager
import re
import sqlite3
import json
import pytest

from movie_collection.models.movies_model import (
    Movie,
    create_movie,
    delete_movie,
    get_movie_by_id,
    get_movie_by_compound_key,
    get_all_movies,
    update_watch_count
)

######################################################
#
#    Fixtures
#
######################################################

TEST_RESPONSE = json.loads('''{"Title":"Guardians of the Galaxy Vol. 2","Year":"2017","Rated":"PG-13","Released":"05 May 2017","Runtime":"136 min","Genre":"Action, Adventure, Comedy","Director":"James Gunn","Writer":"James Gunn, Dan Abnett, Andy Lanning","Actors":"Chris Pratt, Zoe Saldana, Dave Bautista","Plot":"After saving Xandar from Ronan's wrath, the Guardians are now recognized as heroes. Now the team must help their leader Star Lord (Chris Pratt) uncover the truth behind his true heritage. Along the way, old foes turn to allies and betrayal is blooming. And the Guardians find that they are up against a devastating new menace who is out to rule the galaxy.","Language":"English","Country":"United States","Awards":"Nominated for 1 Oscar. 15 wins & 60 nominations total","Poster":"https://m.media-amazon.com/images/M/MV5BNWE5MGI3MDctMmU5Ni00YzI2LWEzMTQtZGIyZDA5MzQzNDBhXkEyXkFqcGc@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"7.6/10"},{"Source":"Rotten Tomatoes","Value":"85%"},{"Source":"Metacritic","Value":"67/100"}],"Metascore":"67","imdbRating":"7.6","imdbVotes":"777,934","imdbID":"tt3896198","Type":"movie","DVD":"N/A","BoxOffice":"$389,813,101","Production":"N/A","Website":"N/A","Response":"True"}'''
)
TEST_IMDB_ID = "tt3896198"
TEST_DIRECTOR = "James Gunn"
TEST_TITLE = "Guardians of the Galaxy Vol. 2"
TEST_GENRE = "Action, Adventure, Comedy"
TEST_YEAR = 2017
TEST_DURATION = 136


def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()


@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("movie_collection.models.movies_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################

def test_create_movie(mock_cursor, mocker):
    """Test creating a new movie in the catalog."""

    mock_omdb_data = mocker.patch("movie_collection.models.movies_model.get_omdb_data", return_value=TEST_RESPONSE)


    # Call the function to create a new movie
    create_movie(title=TEST_TITLE)

    mock_omdb_data.assert_called_once_with(TEST_TITLE)

    expected_query = normalize_whitespace("""
        INSERT INTO movies (imdb_id, director, title, genre, year, duration)
        VALUES (?, ?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (TEST_IMDB_ID, TEST_DIRECTOR, TEST_TITLE, TEST_GENRE, TEST_YEAR, TEST_DURATION)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_movie_duplicate(mock_cursor, mocker):
    """Test creating a movie with a duplicate director, title, and year (should raise an error)."""

    mock_omdb_data = mocker.patch("movie_collection.models.movies_model.get_omdb_data", return_value=TEST_RESPONSE)

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: movies.director, movies.title, movies.year")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match=f"Movie with director '{TEST_DIRECTOR}', title '{TEST_TITLE}', and year {TEST_YEAR} already exists."):
         create_movie(title=TEST_TITLE)

    mock_omdb_data.assert_called_once_with(TEST_TITLE)


def test_delete_movie(mock_cursor):
    """Test soft deleting a movie from the catalog by movie ID."""

    # Simulate that the movie exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_movie function
    delete_movie(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM movies WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE movies SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_movie_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent movie."""

    # Simulate that no movie exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent movie
    with pytest.raises(ValueError, match="Movie with ID 999 not found"):
        delete_movie(999)


def test_delete_movie_already_deleted(mock_cursor):
    """Test error when trying to delete a move that's already marked as deleted."""

    # Simulate that the movie exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a movie that's already been deleted
    with pytest.raises(ValueError, match="Movie with ID 999 has already been deleted"):
        delete_movie(999)

######################################################
#
#    Get Movie
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the movie exists (id = 1)
    mock_cursor.fetchone.return_value = (1, TEST_IMDB_ID, TEST_DIRECTOR, TEST_TITLE, TEST_GENRE, TEST_YEAR, TEST_DURATION, False)

    # Call the function and check the result
    result = get_movie_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Movie(1, TEST_IMDB_ID, TEST_DIRECTOR, TEST_TITLE, TEST_GENRE, TEST_YEAR, TEST_DURATION)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, imdb_id, director, title, genre, year, duration, deleted FROM movies WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_movie_by_id_bad_id(mock_cursor):
    # Simulate that no movie exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the movie is not found
    with pytest.raises(ValueError, match="Movie with ID 999 not found"):
        get_movie_by_id(999)

def test_get_movie_by_compound_key(mock_cursor):
    # Simulate that the movie exists (director = "Director Name", title = "Movie Title", year = 2022)
    mock_cursor.fetchone.return_value = (1, TEST_IMDB_ID, TEST_DIRECTOR, TEST_TITLE, TEST_GENRE, TEST_YEAR, TEST_DURATION, False)

    # Call the function and check the result
    result = get_movie_by_compound_key(TEST_DIRECTOR, TEST_TITLE, TEST_YEAR)

    # Expected result based on the simulated fetchone return value
    expected_result = Movie(1, TEST_IMDB_ID, TEST_DIRECTOR, TEST_TITLE, TEST_GENRE, TEST_YEAR, TEST_DURATION)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, imdb_id, director, title, genre, year, duration, deleted FROM movies WHERE director = ? AND title = ? AND year = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (TEST_DIRECTOR, TEST_TITLE, TEST_YEAR)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_all_movies(mock_cursor):
    """Test retrieving all movies that are not marked as deleted."""

    # Simulate that there are multiple movies in the database
    mock_cursor.fetchall.return_value = [
        (1, "imdb_id1", "Director A", "Movie A", "Comedy", 2022, 120, 10, False),
        (2, "imdb_id2", "Director B", "Movie B", "Romance", 1989, 180, 20, False),
        (3, "imdb_id3", "Director C", "Movie C", "Action",2000, 60, 5, False)
    ]

    # Call the get_all_movies function
    movies = get_all_movies()

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "imdb_id": "imdb_id1", "director": "Director A", "title": "Movie A", "genre": "Comedy", "year":2022, "duration": 120, "watch_count": 10},
        {"id": 2, "imdb_id": "imdb_id2", "director": "Director B", "title": "Movie B", "genre": "Romance", "year": 1989, "duration": 180, "watch_count": 20},
        {"id": 3, "imdb_id": "imdb_id3", "director": "Director C", "title": "Movie C", "genre": "Action", "year":2000, "duration": 60, "watch_count": 5}
    ]

    assert movies == expected_result, f"Expected {expected_result}, but got {movies}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, imdb_id, director, title, genre, year, duration, watch_count
        FROM movies
        WHERE deleted = FALSE
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_movies_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all movies returns an empty list when the catalog is empty and logs a warning."""

    # Simulate that the catalog is empty (no movies)
    mock_cursor.fetchall.return_value = []

    # Call the get_all_movies function
    result = get_all_movies()

    # Ensure the result is an empty list
    assert result == [], f"Expected empty list, but got {result}"

    # Ensure that a warning was logged
    assert "The movie catalog is empty." in caplog.text, "Expected warning about empty catalog not found in logs."

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, imdb_id, director, title, genre, year, duration, watch_count FROM movies WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_movies_ordered_by_watch_count(mock_cursor):
    """Test retrieving all movies ordered by watch count."""

    # Simulate that there are multiple movies in the database
    mock_cursor.fetchall.return_value = [
        (1, "imdb_id1", "Director A", "Movie A", "Comedy", 2022, 120, 10, False),
        (2, "imdb_id2", "Director B", "Movie B", "Romance", 1989, 180, 20, False),
        (3, "imdb_id3", "Director C", "Movie C", "Action",2000, 60, 5, False)
    ]

    # Call the get_all_movies function with sort_by_watch_count = True
    movies = get_all_movies(sort_by_watch_count=True)

    # Ensure the results are sorted by watch count
    expected_result = [
        {"id": 1, "imdb_id": "imdb_id1", "director": "Director A", "title": "Movie A", "genre": "Comedy", "year":2022, "duration": 120, "watch_count": 10},
        {"id": 2, "imdb_id": "imdb_id2", "director": "Director B", "title": "Movie B", "genre": "Romance", "year": 1989, "duration": 180, "watch_count": 20},
        {"id": 3, "imdb_id": "imdb_id3", "director": "Director C", "title": "Movie C", "genre": "Action", "year":2000, "duration": 60, "watch_count": 5}
    ]

    assert movies == expected_result, f"Expected {expected_result}, but got {movies}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, imdb_id, director, title, genre, year, duration, watch_count
        FROM movies
        WHERE deleted = FALSE
        ORDER BY watch_count DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_update_watch_count(mock_cursor):
    """Test updating the watch count of a movie."""

    # Simulate that the movie exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_watch_count function with a sample movie ID
    movie_id = 1
    update_watch_count(movie_id)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE movies SET watch_count = watch_count + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (movie ID)
    expected_arguments = (movie_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

    ## Test for Updating a Deleted Movie:
def test_update_watch_count_deleted_movie(mock_cursor):
    """Test error when trying to update watch count for a deleted movie."""

    # Simulate that the movie exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted movie
    with pytest.raises(ValueError, match="Movie with ID 1 has been deleted"):
        update_watch_count(1)

    # Ensure that no SQL query for updating watch count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM movies WHERE id = ?", (1,))