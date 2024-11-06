import os
import inspect as ins

from configuration import get_configuration
from squotes import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the path to the database file
# DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
configuration = get_configuration()

username = configuration["db_username"]
password = configuration["db_password"]
ip = configuration["db_ip"]
port = configuration["db_port"]
db_enable = configuration["db_enable"]

exposed = [
    "Base",
    "initDB",
    "insertRow",
    "Authors",
    "TestTable",
    "Tags",
    "Quotes",
    "QuotesTagsLink"
]

if db_enable == 0:
    logger.info(f"db is disabled in configuration. database __init__.py's db initialization parts of code ingnored.")
else:
    exposed.append("engine")
    exposed.append("Session")        

    # Create engine with the updated path
    # engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
    ip_and_port = ip + ":" + port
    if port == '':
        ip_and_port = ip

    engine = create_engine(f"mysql+pymysql://{username}:{password}@{ip_and_port}/{configuration["db_name"]}?charset=utf8mb4")


    logger.info(f"Created database engine for db {configuration["db_name"]}, user {username}, address {ip}:{port}")

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Import operations and schema after engine and Base are defined
from .operations import initDB, insertRow
from .schema import TestTable, Tags, Authors, Quotes, QuotesTagsLink


# Expose commonly used functions and classes
__all__ = exposed 
