import pytest
import requests
import os
import json

from movie_collection.utils.omdb_utils import get_omdb_data


TEST_RESPONSE = '''{"Title":"Guardians of the Galaxy Vol. 2","Year":"2017","Rated":"PG-13","Released":"05 May 2017","Runtime":"136 min","Genre":"Action, Adventure, Comedy","Director":"James Gunn","Writer":"James Gunn, Dan Abnett, Andy Lanning","Actors":"Chris Pratt, Zoe Saldana, Dave Bautista","Plot":"After saving Xandar from Ronan's wrath, the Guardians are now recognized as heroes. Now the team must help their leader Star Lord (Chris Pratt) uncover the truth behind his true heritage. Along the way, old foes turn to allies and betrayal is blooming. And the Guardians find that they are up against a devastating new menace who is out to rule the galaxy.","Language":"English","Country":"United States","Awards":"Nominated for 1 Oscar. 15 wins & 60 nominations total","Poster":"https://m.media-amazon.com/images/M/MV5BNWE5MGI3MDctMmU5Ni00YzI2LWEzMTQtZGIyZDA5MzQzNDBhXkEyXkFqcGc@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"7.6/10"},{"Source":"Rotten Tomatoes","Value":"85%"},{"Source":"Metacritic","Value":"67/100"}],"Metascore":"67","imdbRating":"7.6","imdbVotes":"777,934","imdbID":"tt3896198","Type":"movie","DVD":"N/A","BoxOffice":"$389,813,101","Production":"N/A","Website":"N/A","Response":"True"}'''
INVALID_RESPONSE = '''{"Response":"False","Error":"Movie not found!"}'''
TEST_TITLE = "Guardians of the Galaxy Vol. 2"
API_KEY = os.getenv("API_KEY")


@pytest.fixture
def mock_omdb_com(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a text attribute
    mock_response.json.return_value = json.loads(TEST_RESPONSE)
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_data(mock_omdb_com):
    """Test retrieving a random number from random.org."""
    result = get_omdb_data(TEST_TITLE)

    # Assert that the result is the mocked random number
    assert result == json.loads(TEST_RESPONSE), f"Expected {TEST_RESPONSE},\n but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with(f"https://www.omdbapi.com/?t={TEST_TITLE}&apikey={API_KEY}", timeout=5)

def test_get_data_request_failure(mocker):
    """Simulate  a request failure."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to omdbapi.com failed: Connection error"):
        get_omdb_data(TEST_TITLE)

def test_get_data_timeout(mocker):
    """Simulate  a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to omdbapi.com timed out."):
        get_omdb_data(TEST_TITLE)

def test_get_data_invalid_response(mock_omdb_com):
    """Simulate  an invalid response (non-digit)."""
    mock_omdb_com.json.return_value = json.loads(INVALID_RESPONSE)

    with pytest.raises(ValueError, match="Invalid response from omdbapi.com: Movie not found!"):
        get_omdb_data("invalid title")

