import os
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

from movie_collection.models import movies_model
from movie_collection.models.watchlist_model import WatchlistModel
from movie_collection.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

watchlist_model = WatchlistModel()


####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)


@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and movie table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if movies table exists...")
        check_table_exists("movies")
        app.logger.info("movies table exists.")
        check_table_exists("users")
        app.logger.info("users table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

##########################################################
#
# Movie Management
#
##########################################################
@app.route('/api/create-movie', methods=['POST'])
def add_movie() -> Response:
    """
    Route to add a new movie to the watchlist.

    Expected JSON Input:
        - director (str): The director's name.
        - title (str): The movie title.
        - year (int): The year the movie was released.
        - genre (str): The genre of the movie.
        - duration (int): The duration of the movie in minutes.

    Returns:
        JSON response indicating the success of the movie addition.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the movie to the watchlist.
    """
    app.logger.info('Adding a new movie to the catalog')
    try:
        data = request.get_json()
        title = data.get('title')

        if not title:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        app.logger.info('Adding movie: %s', title)
        movies_model.create_movie(title=title)
        app.logger.info("movie created: %s",title)
        return make_response(jsonify({'status': 'success', 'movie': title}), 201)
    except Exception as e:
        app.logger.error("Failed to add movie: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/clear-catalog', methods=['DELETE'])
def clear_catalog() -> Response:
    """
    Route to clear the entire movies catalog (recreates the table).

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info("Clearing the movies catalog")
        movies_model.clear_catalog()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error clearing catalog: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/delete-movie/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id: int) -> Response:
    """
    Route to delete a movie by its ID (soft delete).

    Path Parameter:
        - movie_id (int): The ID of the movie to delete.

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info(f"Deleting movie by ID: {movie_id}")
        movies_model.delete_movie(movie_id)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error deleting movie: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-all-movies-from-catalog', methods=['GET'])
def get_all_movies() -> Response:
    """
    Route to retrieve all movies in the catalog (non-deleted), with an option to sort by play count.

    Query Parameter:
        - sort_by_play_count (bool, optional): If true, sort movies by play count.

    Returns:
        JSON response with the list of movies or error message.
    """
    try:
        # Extract query parameter for sorting by play count
        sort_by_play_count = request.args.get('sort_by_play_count', 'false').lower() == 'true'

        app.logger.info("Retrieving all movies from the catalog, sort_by_play_count=%s", sort_by_play_count)
        movies = movies_model.get_all_movies(sort_by_play_count=sort_by_play_count)

        return make_response(jsonify({'status': 'success', 'movies': movies}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving movies: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-movie-from-catalog-by-id/<int:movie_id>', methods=['GET'])
def get_movie_by_id(movie_id: int) -> Response:
    """
    Route to retrieve a movie by its ID.

    Path Parameter:
        - movie_id (int): The ID of the movie.

    Returns:
        JSON response with the movie details or error message.
    """
    try:
        app.logger.info(f"Retrieving movie by ID: {movie_id}")
        movie = movies_model.get_movie_by_id(movie_id)
        return make_response(jsonify({'status': 'success', 'movie': movie}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving movie by ID: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-movie-from-catalog-by-compound-key', methods=['GET'])
def get_movie_by_compound_key() -> Response:
    """
    Route to retrieve a movie by its compound key (director, title, year).

    Query Parameters:
        - director (str): The director's name.
        - title (str): The movie title.
        - year (int): The year the movie was released.

    Returns:
        JSON response with the movie details or error message.
    """
    try:
        # Extract query parameters from the request
        director = request.args.get('director')
        title = request.args.get('title')
        year = request.args.get('year')

        if not director or not title or not year:
            return make_response(jsonify({'error': 'Missing required query parameters: director, title, year'}), 400)

        # Attempt to cast year to an integer
        try:
            year = int(year)
        except ValueError:
            return make_response(jsonify({'error': 'Year must be an integer'}), 400)

        app.logger.info(f"Retrieving movie by compound key: {director}, {title}, {year}")
        movie = movies_model.get_movie_by_compound_key(director, title, year)
        return make_response(jsonify({'status': 'success', 'movie': movie}), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving movie by compound key: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


############################################################
#
# Watchlist Management
#
############################################################

@app.route('/api/add-movie-to-watchlist', methods=['POST'])
def add_movie_to_watchlist() -> Response:
    """
    Route to add a movie to the watchlist by compound key (director, title, year).

    Expected JSON Input:
        - director (str): The director's name.
        - title (str): The movie title.
        - year (int): The year the movie was released.

    Returns:
        JSON response indicating success of the addition or error message.
    """
    try:
        data = request.get_json()

        director = data.get('director')
        title = data.get('title')
        year = data.get('year')

        if not director or not title or not year:
            return make_response(jsonify({'error': 'Invalid input. Director, title, and year are required.'}), 400)

        # Lookup the movie by compound key
        movie = movies_model.get_movie_by_compound_key(director, title, year)

        # Add movie to watchlist
        watchlist_model.add_movie_to_watchlist(movie)

        app.logger.info(f"movie added to watchlist: {director} - {title} ({year})")
        return make_response(jsonify({'status': 'success', 'message': 'movie added to watchlist'}), 201)

    except Exception as e:
        app.logger.error(f"Error adding movie to watchlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/remove-movie-from-watchlist', methods=['DELETE'])
def remove_movie_by_movie_id() -> Response:
    """
    Route to remove a movie from the watchlist by compound key (director, title, year).

    Expected JSON Input:
        - director (str): The director's name.
        - title (str): The movie title.
        - year (int): The year the movie was released.

    Returns:
        JSON response indicating success of the removal or error message.
    """
    try:
        data = request.get_json()

        director = data.get('director')
        title = data.get('title')
        year = data.get('year')

        if not director or not title or not year:
            return make_response(jsonify({'error': 'Invalid input. director, title, and year are required.'}), 400)

        # Lookup the movie by compound key
        movie = movies_model.get_movie_by_compound_key(director, title, year)

        # Remove movie from watchlist
        watchlist_model.remove_movie_by_movie_id(movie.id)

        app.logger.info(f"movie removed from watchlist: {director} - {title} ({year})")
        return make_response(jsonify({'status': 'success', 'message': 'movie removed from watchlist'}), 200)

    except Exception as e:
        app.logger.error(f"Error removing movie from watchlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/remove-movie-from-watchlist-by-list-number/<int:list_number>', methods=['DELETE'])
def remove_movie_by_list_number(list_number: int) -> Response:
    """
    Route to remove a movie from the watchlist by list number.

    Path Parameter:
        - list_number (int): The list number of the movie to remove.

    Returns:
        JSON response indicating success of the removal or an error message.
    """
    try:
        app.logger.info(f"Removing movie from watchlist by list number: {list_number}")

        # Remove movie by list number
        watchlist_model.remove_movie_by_list_number(list_number)

        return make_response(jsonify({'status': 'success', 'message': f'movie at list number {list_number} removed from watchlist'}), 200)

    except ValueError as e:
        app.logger.error(f"Error removing movie by list number: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error removing movie from watchlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/clear-watchlist', methods=['POST'])
def clear_watchlist() -> Response:
    """
    Route to clear all movies from the watchlist.

    Returns:
        JSON response indicating success of the operation or an error message.
    """
    try:
        app.logger.info('Clearing the watchlist')

        # Clear the entire watchlist
        watchlist_model.clear_watchlist()

        return make_response(jsonify({'status': 'success', 'message': 'watchlist cleared'}), 200)

    except Exception as e:
        app.logger.error(f"Error clearing the watchlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

############################################################
#
# Arrange Watchlist
#
############################################################
############################################################
#
# Leaderboard / Stats
#
############################################################
if __name__ == '__main__':
    port = os.getenv("PORT")
    app.run(debug=True, host='0.0.0.0', port=port)

