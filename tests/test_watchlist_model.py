import pytest
from movie_collection.models.watchlist_model import WatchlistModel
from movie_collection.models.movies_model import Movie


@pytest.fixture()
def watchlist_model():
    """Fixture to provide a new instance of WatchlistModel for each test."""
    return WatchlistModel()

"""Fixtures providing sample movies for the tests."""
@pytest.fixture
def sample_movie1():
    return Movie(1, "Director 1", "Movie 1", 2022, "Drama", 120)

@pytest.fixture
def sample_movie2():
    return Movie(2, "Director 2", "Movie 2", 2021, "Comedy", 90)

@pytest.fixture
def sample_watchlist(sample_movie1, sample_movie2):
    return [sample_movie1, sample_movie2]


##################################################
# Add Movie Management Test Cases
##################################################

def test_add_movie_to_watchlist(watchlist_model, sample_movie1):
    """Test adding a movie to the watchlist."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    assert len(watchlist_model.watchlist) == 1
    assert watchlist_model.watchlist[0].title == "Movie 1"

def test_add_duplicate_movie_to_watchlist(watchlist_model, sample_movie1):
    """Test error when adding a duplicate movie to the watchlist by ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    with pytest.raises(ValueError, match="Movie with ID 1 already exists in the watchlist"):
        watchlist_model.add_movie_to_watchlist(sample_movie1)

##################################################
# Remove Movie Management Test Cases
##################################################

def test_remove_movie_from_watchlist_by_movie_id(watchlist_model, sample_watchlist):
    """Test removing a movie from the watchlist by movie_id."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert len(watchlist_model.watchlist) == 2

    watchlist_model.remove_movie_by_id(1)
    assert len(watchlist_model.watchlist) == 1
    assert watchlist_model.watchlist[0].id == 2

def test_clear_watchlist(watchlist_model, sample_movie1):
    """Test clearing the entire watchlist."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0

##################################################
# Watchlist Retrieval Test Cases
##################################################

def test_get_all_movies(watchlist_model, sample_watchlist):
    """Test successfully retrieving all movies from the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    all_movies = watchlist_model.get_all_movies()
    assert len(all_movies) == 2
    assert all_movies[0].id == 1
    assert all_movies[1].id == 2

def test_get_movie_by_id(watchlist_model, sample_movie1):
    """Test successfully retrieving a movie from the watchlist by movie ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    retrieved_movie = watchlist_model.get_movie_by_id(1)

    assert retrieved_movie.id == 1
    assert retrieved_movie.title == "Movie 1"

def test_get_current_movie(watchlist_model, sample_watchlist):
    """Test successfully retrieving the current movie from the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    current_movie = watchlist_model.get_current_movie()
    assert current_movie.id == 1
    assert current_movie.title == "Movie 1"

##################################################
# Watchlist Ordering Test Cases
##################################################

def test_move_movie_to_beginning(watchlist_model, sample_watchlist):
    """Test moving a movie to the beginning of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_beginning(2)  # Move Movie 2 to the beginning
    assert watchlist_model.watchlist[0].id == 2
    assert watchlist_model.watchlist[1].id == 1

def test_move_movie_to_end(watchlist_model, sample_watchlist):
    """Test moving a movie to the end of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_end(1)  # Move Movie 1 to the end
    assert watchlist_model.watchlist[1].id == 1

##################################################
# Utility Function Test Cases
##################################################

def test_check_if_empty_non_empty_watchlist(watchlist_model, sample_movie1):
    """Test check_if_empty does not raise error if watchlist is not empty."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    try:
        watchlist_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty watchlist")

def test_check_if_empty_empty_watchlist(watchlist_model):
    """Test check_if_empty raises error when watchlist is empty."""
    watchlist_model.clear_watchlist()
    with pytest.raises(ValueError, match="Watchlist is empty"):
        watchlist_model.check_if_empty()
