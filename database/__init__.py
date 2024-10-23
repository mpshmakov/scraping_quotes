import os

from configuration import get_configuration
from sbooks import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the path to the database file
# DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
configuration = get_configuration()
DATA_DIR = os.path.abspath(configuration["db_path"])
DB_PATH = os.path.join(DATA_DIR, configuration["db_filename"] + ".db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Ensured data directory exists at {DATA_DIR}")

# Create engine with the updated path
# engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
engine = create_engine(f"mysql+pymysql://root:@localhost/{configuration["db_filename"]}?charset=utf8mb4")

# TODO: remove if decide to use mysql
# from sqlalchemy import event
# from sqlalchemy.engine import Engine

# from sqlite3 import Connection as SQLite3Connection

# @event.listens_for(Engine, "connect")
# def _set_sqlite_pragma(dbapi_connection, connection_record):
#     if isinstance(dbapi_connection, SQLite3Connection):
#         cursor = dbapi_connection.cursor()
#         cursor.execute("PRAGMA foreign_keys=ON;")
#         cursor.close()


# def _fk_pragma_on_connect(dbapi_con, con_record):
#     dbapi_con.execute('pragma foreign_keys=ON')

# event.listen(engine, 'connect', _fk_pragma_on_connect)



logger.info(f"Created database engine for {DB_PATH}")

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Import operations and schema after engine and Base are defined
from .operations import initDB, insertRow
from .schema import TestTable, Tags, Authors, Quotes, QuotesTagsLink

# Expose commonly used functions and classes
__all__ = [
    "engine",
    "Session",
    "Base",
    "initDB",
    "insertRow",
    "Authors",
    "TestTable",
    "Tags",
    "Quotes",
    "QuotesTagsLink"
]
