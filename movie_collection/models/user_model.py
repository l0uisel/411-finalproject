import logging
import sqlite3
from bcrypt import gensalt, hashpw, checkpw
from movie_collection.utils.sql_utils import get_db_connection
from movie_collection.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


def hash_password(password: str, salt: str) -> str:
    """
    Hashes a password using the provided salt.
    """
    return hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

def validate_password(stored_hashed_password: str, password: str) -> bool:
    """
    Validates the provided password against the stored hashed password.
    """
    return checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8'))

def create_user(username: str, password: str) -> None:
    """
    Creates a new user in the database.

    Args:
        username (str): The username.
        password (str): The plaintext password.

    Raises:
        ValueError: If the username already exists or another error occurs.
    """
    logger.info("Attempting to create a new user: %s", username)
    salt = gensalt().decode('utf-8')
    hashed_password = hash_password(password, salt)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, salt, hashed_password)
                VALUES (?, ?, ?)
            """, (username, salt, hashed_password))
            conn.commit()
            logger.info("User %s created successfully.", username)
    except sqlite3.IntegrityError:
        logger.error("User %s already exists.", username)
        raise ValueError(f"User {username} already exists.")
    except sqlite3.Error as e:
        logger.error("Database error while creating user: %s", e)
        raise ValueError(f"Database error: {e}")

def validate_user(username: str, password: str) -> bool:
    """
    Validates a user's credentials.

    Args:
        username (str): The username.
        password (str): The plaintext password.

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    logger.info("Validating credentials for user: %s", username)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hashed_password
                FROM users
                WHERE username = ?
            """, (username,))
            row = cursor.fetchone()

            if row:
                is_valid = validate_password(row[0], password)
                if is_valid:
                    logger.info("Credentials for user %s are valid.", username)
                else:
                    logger.warning("Invalid credentials for user %s.", username)
                return is_valid
            else:
                logger.warning("User %s not found.", username)
                return False
    except sqlite3.Error as e:
        logger.error("Database error during user validation: %s", e)
        return False

def update_password(username: str, old_password:str, new_password: str) -> None:
    """
    Updates a user's password.

    Args:
        username (str): The username of the user.
        old_password (str): The old plaintext password.
        new_password (str): The new plaintext password.

    Raises:
        ValueError: If the user does not exist or another error occurs.
    """
    logger.info("Attempting to update password for user: %s", username)
    new_salt = gensalt().decode('utf-8')
    new_hashed_password = hash_password(new_password, new_salt)

    if not validate_user(username, old_password):
        logger.warning("Invalid credentials while updating password for user %s.", username)
        raise ValueError("Invalid credentials.")
    else:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET salt = ?, hashed_password = ?
                    WHERE username = ?
                """, (new_salt, new_hashed_password, username))
                if cursor.rowcount == 0:
                    logger.warning("User %s not found while updating password.", username)
                    raise ValueError(f"User {username} not found.")
                conn.commit()
                logger.info("Password for user %s updated successfully.", username)
        except sqlite3.Error as e:
            logger.error("Database error while updating password for user %s: %s", username, e)
            raise ValueError(f"Database error: {e}")
