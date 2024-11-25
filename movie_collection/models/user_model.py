import logging
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from bcrypt import gensalt, hashpw, checkpw
import os
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)
# configure_logger(logger)

# SQLAlchemy setup
DB_PATH = os.getenv("DB_PATH", "sqlite:///app/db/movie_catalog.db")  # Default to SQLite if no environment variable
ENCODING = os.getenv("ENCODING", "utf-8")
engine = create_engine(DB_PATH, echo=False)  # Set echo=True for SQL logging during development
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()


# Context manager for database sessions
@contextmanager
def get_db_session() -> Session:
    """
    Provides a database session as a context manager.
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error("Database connection error: %s", str(e))
        raise e
    finally:
        session.close()
        logger.info("Database connection closed.")


# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    salt = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


def validate_user(username: str, password: str) -> bool:
    """
    Validates a user's credentials.

    Args:
        username (str): The username.
        password (str): The plaintext password.

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """
    logger.info("Validating credentials for user: %s", username)
    try:
        with get_db_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                logger.warning("User %s not found during validation.", username)
                return False

            is_valid = checkpw(password.encode(ENCODING), user.hashed_password.encode(ENCODING))
            if is_valid:
                logger.info("Credentials for user %s are valid.", username)
            else:
                logger.warning("Invalid credentials for user %s.", username)
            return is_valid
    except Exception as e:
        logger.error("Error validating credentials for user %s: %s", username, e)
        return False


def create_user(username: str, password: str) -> None:
    """
    Creates a new user.

    Args:
        username (str): The username.
        password (str): The plaintext password.

    Raises:
        ValueError: If the username already exists.
    """
    logger.info("Attempting to create a new user: %s", username)
    salt = gensalt().decode(ENCODING)
    hashed_password = hashpw(password.encode(ENCODING), salt.encode(ENCODING)).decode(ENCODING)

    user = User(username=username, salt=salt, hashed_password=hashed_password)

    try:
        with get_db_session() as session:
            session.add(user)
            session.commit()
            logger.info("User %s created successfully.", username)
    except Exception as e:
        logger.error("Error creating user %s: %s", username, e)
        raise ValueError(f"Error creating user: {e}") from e


def update_password(username: str, new_password: str) -> None:
    """
    Updates a user's password.

    Args:
        username (str): The username of the user whose password is being updated.
        new_password (str): The new plaintext password.

    Raises:
        ValueError: If the user does not exist.
    """
    logger.info("Attempting to update password for user: %s", username)
    new_salt = gensalt().decode(ENCODING)
    new_hashed_password = hashpw(new_password.encode(ENCODING), new_salt.encode(ENCODING)).decode(ENCODING)

    try:
        with get_db_session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                logger.warning("User %s not found while updating password.", username)
                raise ValueError(f"User {username} not found.")

            user.salt = new_salt
            user.hashed_password = new_hashed_password
            session.commit()
            logger.info("Password for user %s updated successfully.", username)
    except Exception as e:
        logger.error("Error updating password for user %s: %s", username, e)
        raise ValueError(f"Error updating password: {e}") from e
