import pytest
import sqlite3
import re
import os
from contextlib import contextmanager
from unittest.mock import patch, MagicMock, ANY
from bcrypt import gensalt, hashpw
from movie_collection.models.user_model import (
    hash_password,
    validate_password,
    create_user,
    validate_user,
    update_password,
)

ENCODING = os.getenv("ENCODING")

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.Mock()  # Mock the database connection
    mock_cursor = mocker.Mock()  # Mock the cursor object

    # Configure the mock connection to return the mock cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default for SELECT queries
    mock_cursor.fetchall.return_value = []    # Default for SELECT queries returning multiple rows
    mock_conn.commit.return_value = None      # Mock commit behavior

    # Mock the `get_db_connection` context manager
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    # Patch `get_db_connection` in the user model's module
    mocker.patch("movie_collection.models.user_model.get_db_connection", mock_get_db_connection)

    return mock_conn  # Return the mock connection for test-specific configuration

def test_hash_password():
    salt = gensalt().decode(ENCODING)
    password = "securepassword"
    hashed = hash_password(password, salt)
    assert hashpw(password.encode(ENCODING), salt.encode(ENCODING)).decode(ENCODING) == hashed

def test_validate_password():
    password = "securepassword"
    salt = gensalt().decode(ENCODING)
    hashed = hash_password(password, salt)
    assert validate_password(hashed, password) is True
    assert validate_password(hashed, "wrongpassword") is False

def test_create_user_success(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.fetchone.return_value = None

    username = "newuser"
    password = "securepassword"

    create_user(username, password)

    expected_query = normalize_whitespace("""
            INSERT INTO users (username, salt, hashed_password)
            VALUES (?, ?, ?)
        """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (username, ANY, ANY)  # salt and hashed_password should be generated dynamically
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_user_existing(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.IntegrityError

    username = "existinguser"
    password = "securepassword"

    with pytest.raises(ValueError, match=f"User {username} already exists."):
        create_user(username, password)

def test_validate_user_success(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    hashed_password = hash_password("securepassword", gensalt().decode(ENCODING))
    mock_cursor.fetchone.return_value = (hashed_password,)

    assert validate_user("testuser", "securepassword") is True

def test_validate_user_invalid(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    hashed_password = hash_password("securepassword", gensalt().decode(ENCODING))
    mock_cursor.fetchone.return_value = (hashed_password,)

    assert validate_user("testuser", "wrongpassword") is False

def test_validate_user_not_found(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.fetchone.return_value = None

    assert validate_user("nonexistent", "securepassword") is False

def test_update_password_success(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.rowcount = 1

    username = "existinguser"
    new_password = "newsecurepassword"

    update_password(username, new_password)

    # Define the expected query
    expected_query = normalize_whitespace("""
            UPDATE users
            SET salt = ?, hashed_password = ?
            WHERE username = ?
        """)

    # Normalize the query for comparison
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query is as expected
    assert actual_query == normalize_whitespace(expected_query), "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (ANY, ANY, username)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_password_user_not_found(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.rowcount = 0

    username = "nonexistentuser"
    new_password = "newsecurepassword"

    with pytest.raises(ValueError, match=f"User {username} not found."):
        update_password(username, new_password)

def test_update_password_database_error(mock_db_connection):
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.execute.side_effect = sqlite3.Error("Mock database error")

    username = "existinguser"
    new_password = "newsecurepassword"

    with pytest.raises(ValueError, match="Database error: Mock database error"):
        update_password(username, new_password)
