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