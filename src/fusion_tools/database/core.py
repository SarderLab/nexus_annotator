"""
Database setup and session management using SQLAlchemy.

This module configures the SQLAlchemy engine, provides a context-managed session,
and initializes the database schema.

Environment variables:
    DATABASE_PATH: (optional) Absolute path or directory to store the SQLite database.
"""

import os
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession

from .models import Base  # Import your declarative Base

# --- Constants ---
_DATABASE_NAME = "fusion_tools_activity.db"
_DATABASE_ENV_VAR = "DATABASE_PATH"
_APP_FOLDER_WIN = "FusionTools"
_APP_FOLDER_UNIX = ".local/share/FusionTools"

# --- Logging Configuration ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Database URL Resolution ---
def _get_database_url() -> str:
    """Resolve the database file location based on environment variables and OS."""
    env_path = os.environ.get(_DATABASE_ENV_VAR)
    if env_path:
        env_path = os.path.abspath(env_path)
        if os.path.isdir(env_path):
            db_path = os.path.join(env_path, _DATABASE_NAME)
        else:
            db_path = env_path
    else:
        if os.name == "nt":
            base_dir = os.path.join(
                os.environ.get("APPDATA", os.path.expanduser("~")), _APP_FOLDER_WIN
            )
        else:
            base_dir = os.path.join(os.path.expanduser("~"), _APP_FOLDER_UNIX)
        try:
            os.makedirs(base_dir, exist_ok=True)
        except OSError as exc:
            logger.exception("Failed to create app data directory: %s", base_dir)
            base_dir = os.getcwd()
        db_path = os.path.join(base_dir, _DATABASE_NAME)
    return f"sqlite:///{db_path}"

_DATABASE_URL = _get_database_url()

# --- SQLAlchemy Engine and Session Setup ---
try:
    engine = create_engine(
        _DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for verbose SQL debugging.
    )
except Exception as exc:
    logger.critical("Failed to create SQLAlchemy engine.", exc_info=True)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_database() -> None:
    """Create all database tables if they do not exist.

    Raises:
        SQLAlchemyError: If table creation fails.
    """
    try:
        logger.info("Initializing database schema at %s", _DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as exc:
        logger.exception("Failed to initialize database schema.")
        raise

@contextmanager
def get_db() -> Generator[SQLAlchemySession, None, None]:
    """Yield a SQLAlchemy session, ensuring cleanup and rollback on error.

    Yields:
        SQLAlchemySession: The SQLAlchemy database session.

    Raises:
        Exception: Propagates exceptions raised in the session block.
    """
    db: SQLAlchemySession = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Session rollback due to exception.")
        raise
    finally:
        db.close()
