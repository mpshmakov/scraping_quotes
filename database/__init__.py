import os

from configuration import db_filename, db_path
from sbooks import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the path to the database file
# DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_DIR = os.path.abspath(db_path)
DB_PATH = os.path.join(DATA_DIR, db_filename + ".db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Ensured data directory exists at {DATA_DIR}")

# Create engine with the updated path
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
logger.info(f"Created database engine for {DB_PATH}")

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Import operations and schema after engine and Base are defined
from .operations import initDB, insertRow
from .schema import Books, TestTable

# Expose commonly used functions and classes
__all__ = [
    "engine",
    "Session",
    "Base",
    "initDB",
    "insertRow",
    "Books",
    "TestTable",
]
