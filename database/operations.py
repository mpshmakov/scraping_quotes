"""Database operations module.

This module provides functions for initializing the database schema,
checking table existence, inserting records into the database, and truncating tables.
"""

from configuration import get_configuration
from squotes import logger
from sqlalchemy import MetaData, Table, inspect, select, update, exc
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext


from . import db_enable
if db_enable == 1:
    from . import Base, Session, engine
from .schema import  ApiLogs, TestTable, Authors, Quotes, QuotesTagsLink, Tags, Users

import inspect as ins

def initialize_schema():
    """
    Initialize the database schema by creating required tables.

    Raises:
        SQLAlchemyError: If there's an error during schema initialization.
    """
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return

    try:
        metadata = MetaData()
        # Explicitly define tables
        Table(Tags.__tablename__, metadata, *[c.copy() for c in Tags.__table__.columns],)
        Table(Authors.__tablename__, metadata, *[c.copy() for c in Authors.__table__.columns],)
        Table(Quotes.__tablename__, metadata, *[c.copy() for c in Quotes.__table__.columns],)
        Table(QuotesTagsLink.__tablename__, metadata, *[c.copy() for c in QuotesTagsLink.__table__.columns],)
        Table(Users.__tablename__, metadata, *[c.copy() for c in Users.__table__.columns],)
        Table(ApiLogs.__tablename__, metadata, *[c.copy() for c in ApiLogs.__table__.columns],)
        Table(TestTable.__tablename__, metadata, *[c.copy() for c in TestTable.__table__.columns],)


        # Create tables
        metadata.create_all(engine)
        logger.info("Database schema initialized successfully.")

        # Verify tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in the database: {tables}")

        if "quotes" in tables and "authors" in tables and "quotes_tags_link" in tables and "tags" in tables and  "TestTable" in tables:
            logger.info("All required tables have been created successfully.")
        else:
            logger.error("Not all required tables were created.")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database schema: {str(e)}")
        raise


def check_tables_exist():
    """
    Check if required tables exist in the database.

    Returns:
        bool: True if all required tables exist, False otherwise.

    Raises:
        SQLAlchemyError: If there's an error during inspecting engine.
    """
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return

    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
    except SQLAlchemyError as e:
        logger.error(f"Error inspecting database engine: {str(e)}")
        raise

    required_tables = ["quotes", "tags", "authors", "quotes_tags_link", "users", "apilogs", "TestTable"]
    return all(table in existing_tables for table in required_tables)


def truncate_tables(session):
    """
    Truncate all tables in the database.

    Args:
        session (Session): SQLAlchemy session object.

    Raises:
        SQLAlchemyError: If there's an error during table truncation.
    """
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return

    for table in [Quotes, Authors, Tags, QuotesTagsLink, TestTable]:
        try:
            session.query(table).delete()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error truncating table: {str(e)}")
            raise

    logger.info("All tables truncated successfully.")


def insert_records(session, records, commit=True):
    """
    Insert multiple records into the database.

    Args:
        session (Session): SQLAlchemy session object.
        records (list): List of record objects to be inserted.
        commit (bool): Whether to commit the session after insertion.

    Raises:
        SQLAlchemyError: If there's an error during record insertion.
    """
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return

    try:
        session.add_all(records)
        if commit:
            session.commit()
        logger.info(f"{len(records)} records inserted successfully.")
    except SQLAlchemyError as e:
        if commit:
            session.rollback()
        logger.error(f"Error inserting records: {str(e)}")
        raise


def initDB(truncate = True):
    """
    Initialize the database by creating schema, truncating existing tables, and inserting initial records.

    Args:
        records (list): List of record objects to be inserted after schema creation.

    Raises:
        Exception: If an unexpected error occurs during database initialization.
    """
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return

    try:
        # Initialize the schema first
        initialize_schema()

        # Check if tables exist
        if not check_tables_exist():
            logger.error("Tables were not created successfully.")
            return

        if (truncate == False):
            return
        session = Session()
        try:
            # Truncate existing tables
            truncate_tables(session)

            # Insert new records without committing
            #insert_records(session, records, commit=False)

            # Commit all changes in a single transaction
            session.commit()
            logger.info("Database initialized successfully with new records.")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error during database initialization: {str(e)}")
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during database initialization: {str(e)}"
        )
        raise


def insertRow(row):
    """
    Insert a single row into the database.

    Args:
        row: The row object to be inserted.

    Raises:
        SQLAlchemyError: If there's an error during row insertion.
    """
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return

    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot insert row.")
        return

    session = Session()
    # session.autoflush = False
    try:
        session.add(row)
        session.flush()
        session.commit()
        logger.info(f"Row inserted successfully into {row.__tablename__}.")
    except exc.IntegrityError as e:
        session.rollback()
        logger.warning(f"Integrity error (probably normal behaviour): {str(e)}")
        #print("integrity error")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error inserting row into {row.__tablename__}: {str(e)}")
        raise 

    finally:
        session.close()

def updateAuthorRowAboutValue(author: str, about_text: str):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot insert row.")
        return

    session = Session()
    try:
        #print("updating ", author)
        res =  session.execute(select(Authors).filter_by(author=author)).scalar_one() 
        #print("updateD ", author)
        res.about = about_text
        session.flush()
        session.commit()
        logger.info(f"Row for {author} updated successfully.")
    # except exc.NoResultFound as e:
    #     session.rollback()
    #     #print("NoResultFound error for this author: ", author)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating {author} row: {str(e)}")
        raise
    finally:
        session.close()

def executeOrmStatement(statement):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return

    session = Session()
    try:
        res = session.execute(statement)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error executing statement '{statement}': {str(e)}")
        # raise        

    return res   

def toggleAccessForUser(user_id):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return

    access = 0
    session = Session()
    try:
        res = session.query(Users).filter(Users.id == user_id).scalar()
        if res is None:
            logger.error(f"User with id {user_id} does not exist.")
            return
        print(user_id)
        # print(res[0].id, res[1].id)
        b = not bool(res.access)
        print("b", b)
        res.access = int(b)
        access = int(b)
        print("access = ", access)
        # print(res)
        session.flush()
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error toggling user's access statement. user's id: '{user_id}': {str(e)}")
        raise
    return access

def changeUserPassword(user_id, new_password, old_password):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return
    bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    session = Session()
    try:
        res = session.query(Users).filter(Users.id == user_id).scalar()
        if res is None:
            logger.error(f"User with id {user_id} does not exist.")
            return
        print(old_password, res.password)
        print (bcrypt_context.verify(old_password, res.password))
        if bcrypt_context.verify(old_password, res.password):
            res.password = new_password
            session.flush()
            session.commit()
        else:
            raise ValueError("Old password doesn't match")

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error changing user's access statement. user's id: '{user_id}': {str(e)}")
        raise


def getModelFromTablename(tablename):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c