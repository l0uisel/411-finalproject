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
    return Movie(1, 1, 'Director 1', 'Movie 1', 2022, 'Drama', 180)

@pytest.fixture
def sample_movie2():
    return Movie(2, 2, 'Director 2', 'Movie 2', 2021, 'Comedy', 155)

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
    assert watchlist_model.watchlist[0].title == 'Movie 1'

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

    watchlist_model.remove_movie_by_movie_id(1)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 movie, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0].id == 2, "Expected movie with id 2 to remain"

def test_remove_movie_by_list_number(watchlist_model, sample_watchlist):
    """Test removing a movie from the watchlist by list number."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert len(watchlist_model.watchlist) == 2

    # Remove movie at list number 1 (first movie)
    watchlist_model.remove_movie_by_list_number(1)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 movie, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0].id == 2, "Expected movie with id 2 to remain"

def test_clear_watchlist(watchlist_model, sample_movie1):
    """Test clearing the entire watchlist."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0, "Watchlist should be empty after clearing"

def test_clear_watchlist_empty_watchlist(watchlist_model, caplog):
    """Test clearing the entire watchlist when it's empty."""
    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0, "Watchlist should be empty after clearing"
    assert "Clearing an empty watchlist" in caplog.text, "Expected warning message when clearing an empty watchlist"

##################################################
# Watchlisting Management Test Cases
##################################################

def test_move_movie_to_list_number(watchlist_model, sample_watchlist):
    """Test moving a movie to a specific list number in the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_list_number(2, 1)  # Move Movie 2 to the first position
    assert watchlist_model.watchlist[0].id == 2, "Expected Movie 2 to be in the first position"
    assert watchlist_model.watchlist[1].id == 1, "Expected Movie 1 to be in the second position"

def test_swap_movies_in_watchlist(watchlist_model, sample_watchlist):
    """Test swapping the positions of two movies in the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.swap_movies_in_watchlist(1, 2)  # Swap positions of Movie 1 and Movie 2
    assert watchlist_model.watchlist[0].id == 2, "Expected Movie 2 to be in the first position"
    assert watchlist_model.watchlist[1].id == 1, "Expected Movie 1 to be in the second position"

def test_swap_movie_with_itself(watchlist_model, sample_movie1):
    """Test swapping the position of a movie with itself raises an error."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    with pytest.raises(ValueError, match="Cannot swap a movie with itself"):
        watchlist_model.swap_movies_in_watchlist(1, 1)  # Swap positions of Movie 1 with itself

def test_move_movie_to_end(watchlist_model, sample_watchlist):
    """Test moving a movie to the end of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_end(1)  # Move Movie 1 to the end
    assert watchlist_model.watchlist[1].id == 1, "Expected Movie 1 to be at the end"

def test_move_movie_to_beginning(watchlist_model, sample_watchlist):
    """Test moving a movie to the beginning of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_beginning(2)  # Move Movie 2 to the beginning
    assert watchlist_model.watchlist[0].id == 2, "Expected Movie 2 to be at the beginning"

##################################################
# Movie Retrieval Test Cases
##################################################

def test_get_movie_by_list_number(watchlist_model, sample_watchlist):
    """Test successfully retrieving a movie from the watchlist by list number."""
    watchlist_model.watchlist.extend(sample_watchlist)

    retrieved_movie = watchlist_model.get_movie_by_list_number(1)
    assert retrieved_movie.id == 1
    assert retrieved_movie.title == 'Movie 1'
    assert retrieved_movie.artist == 'Director 1'
    assert retrieved_movie.year == 2022
    assert retrieved_movie.duration == 180
    assert retrieved_movie.genre == 'Drama'

def test_get_all_movies(watchlist_model, sample_watchlist):
    """Test successfully retrieving all movies from the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    all_movies = watchlist_model.get_all_movies()
    assert len(all_movies) == 2
    assert all_movies[0].id == 1
    assert all_movies[1].id == 2

def test_get_movie_by_movie_id(watchlist_model, sample_movie1):
    """Test successfully retrieving a movie from the watchlist by movie ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    retrieved_movie = watchlist_model.get_movie_by_movie_id(1)

    assert retrieved_movie.id == 1
    assert retrieved_movie.title == 'Movie 1'
    assert retrieved_movie.artist == 'Director 1'
    assert retrieved_movie.year == 2022
    assert retrieved_movie.duration == 180
    assert retrieved_movie.genre == 'Drama'

def test_get_current_movie(watchlist_model, sample_watchlist):
    """Test successfully retrieving the current movie from the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    current_movie = watchlist_model.get_current_movie()
    assert current_movie.id == 1
    assert current_movie.title == 'Movie 1'
    assert current_movie.artist == 'Director 1'
    assert current_movie.year == 2022
    assert current_movie.duration == 180
    assert current_movie.genre == 'Drama'

def test_get_watchlist_length(watchlist_model, sample_watchlist):
    """Test getting the length of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert watchlist_model.get_watchlist_length() == 2, "Expected watchlist length to be 2"

def test_get_watchlist_duration(watchlist_model, sample_watchlist):
    """Test getting the total duration of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert watchlist_model.get_watchlist_duration() == 335, "Expected watchlist duration to be 360 minutes"

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

def test_validate_movie_id(watchlist_model, sample_movie1):
    """Test validate_movie_id does not raise error for valid movie ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    try:
        watchlist_model.validate_movie_id(1)
    except ValueError:
        pytest.fail("validate_movie_id raised ValueError unexpectedly for valid movie ID")

def test_validate_movie_id_no_check_in_watchlist(watchlist_model):
    """Test validate_movie_id does not raise error for valid movie ID when the id isn't in the watchlist."""
    try:
        watchlist_model.validate_movie_id(1, check_in_watchlist=False)
    except ValueError:
        pytest.fail("validate_movie_id raised ValueError unexpectedly for valid movie ID")

def test_validate_movie_id_invalid_id(watchlist_model):
    """Test validate_movie_id raises error for invalid movie ID."""
    with pytest.raises(ValueError, match="Invalid movie id: -1"):
        watchlist_model.validate_movie_id(-1)

    with pytest.raises(ValueError, match="Invalid movie id: invalid"):
        watchlist_model.validate_movie_id("invalid")

def test_validate_list_number(watchlist_model, sample_movie1):
    """Test validate_list_number does not raise error for valid list number."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    try:
        watchlist_model.validate_list_number(1)
    except ValueError:
        pytest.fail("validate_list_number raised ValueError unexpectedly for valid list number")

def test_validate_list_number_invalid(watchlist_model, sample_movie1):
    """Test validate_list_number raises error for invalid list number."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    with pytest.raises(ValueError, match="Invalid list number: 0"):
        watchlist_model.validate_list_number(0)

    with pytest.raises(ValueError, match="Invalid list number: 2"):
        watchlist_model.validate_list_number(2)

    with pytest.raises(ValueError, match="Invalid list number: invalid"):
        watchlist_model.validate_list_number("invalid")