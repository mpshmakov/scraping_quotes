"""Database operations module.

This module provides functions for initializing the database schema,
checking table existence, inserting records into the database, and truncating tables.
"""

from datetime import datetime, timedelta
import random
import secrets
import string
from configuration import get_configuration
from squotes import logger
from sqlalchemy import MetaData, Table, delete, insert, inspect, select, update, exc, event, DDL
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext


from . import db_enable
if db_enable == 1:
    from . import Base, Session, engine
from .schema import  ApiLogs, TestTable, Authors, Quotes, QuotesTagsLink, Tags, Users, ConfirmationCodes

import inspect as ins

retention_policy = timedelta(weeks=104) # 2 years
# retention_policy = timedelta(hours=1)

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
        Table(ConfirmationCodes.__tablename__, metadata, *[c.copy() for c in ConfirmationCodes.__table__.columns],)



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

# def create_triggers():
#     update_code_function = DDL('''
#     CREATE FUNCTION update_code_if_old() RETURNS TRIGGER
#     BEGIN
#         IF (NEW.timestamp < NOW() - INTERVAL 3 MINUTE) THEN
#             SET NEW.code = FLOOR(1000 + RAND() * 9000);
#             SET NEW.timestamp = NOW();
#         END IF;
#         RETURN NEW;
#     END;
#     ''')

#     update_code_trigger_insert = DDL('''
#     CREATE TRIGGER update_code_before_insert
#     BEFORE INSERT ON confirm_codes
#     FOR EACH ROW
#     BEGIN
#         CALL update_code_if_old();
#     END;
#     ''')

#     update_code_trigger_update = DDL('''
#     CREATE TRIGGER update_code_before_update
#     BEFORE UPDATE ON confirm_codes
#     FOR EACH ROW
#     BEGIN
#         CALL update_code_if_old();
#     END;
#     ''')

#     event.listen(ConfirmationCodes.__table__, 'after_create', update_code_function)
#     event.listen(ConfirmationCodes.__table__, 'after_create', update_code_trigger_insert)
#     event.listen(ConfirmationCodes.__table__, 'after_create', update_code_trigger_update)

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

    for table in [Quotes, Authors, Tags, QuotesTagsLink, TestTable, ApiLogs, ConfirmationCodes, Users]:
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
        # create_triggers()
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
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error executing statement '{statement}': {str(e)}")
        # raise        

    return res   

def toggleAccessForUser(user_id, stripe_id=None, access=None):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return

    _access = 0
    session = Session()
    try:
        if stripe_id is not None:
            res = session.query(Users).filter(Users.stripe_id == stripe_id).scalar()
        else:    
            res = session.query(Users).filter(Users.id == user_id).scalar()
        if res is None:
            logger.error(f"User with id {user_id} does not exist.")
            return
        print(user_id)
        # print(res[0].id, res[1].id)
        if access is not None:
            res.access = access
            _access = access
        else:
            b = not bool(res.access)
            print("b", b)
            res.access = int(b)
            _access = int(b)
        print("access = ", _access)
        # print(res)
        session.flush()
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error toggling user's access statement. user's id: '{user_id}': {str(e)}")
        raise
    finally:
        session.close()
    return _access

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
        logger.error(f"Error changing user's password. user's id: '{user_id}': {str(e)}")
        raise
    finally:
        session.close()

def generateAndUpdateUserPassword(email):
    bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(random.randrange(15,25)))
    hashed_password = bcrypt_context.hash(password)

    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return
    
    session = Session()
    try:
        res = session.query(Users).filter(Users.email == email).scalar()
        if res is None:
            logger.error(f"User {email} does not exist.")
            raise ValueError(f"User {email} does not exist.")
            return
       
        res.password = hashed_password
        session.flush()
        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error changing user's password. user: '{email}': {str(e)}")
        raise
    finally:
        session.close()

    return password


def generateAndUpdateConfirmCodeForUser(email):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return

    code = random.randrange(1000,9999)
    session = Session()
    try:
        u = session.query(Users).filter(Users.email == email).scalar()
        if u is None:
            logger.error(f"User {email} does not exist.")
            return
        
        res = session.query(ConfirmationCodes).filter(ConfirmationCodes.email == email).scalar()

        if res is None:
            row = ConfirmationCodes(email=email, code=code)
            insertRow(row)
            
        else: 
            res.code = code

        session.flush()
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error toggling user's access statement. user: '{email}': {str(e)}")
        raise
    finally:
        session.close()
    return code

def authenticateConfirmCodeAndResetIt(email, code):
    if db_enable == 0:
        logger.info(f"db is disabled in configuration. {ins.stack()[0][3]} ignored.")
        return
    
    if not check_tables_exist():
        logger.error("Tables do not exist. Cannot retrieve records.")
        return
    result = False
    session = Session()
    try:
        res = session.query(ConfirmationCodes).filter(ConfirmationCodes.email == email).scalar()

        if res is None:
            logger.error(f"Code for {email} does not exist.")
            return result
        
        print(f"code for {email}",res.code)
        print("req code", code)

        if res.timestamp < (datetime.utcnow()-timedelta(minutes=3)):
            res.code = random.randrange(1000, 9999)
        if res.code == code:
            result = True
            res.code = random.randrange(1000, 9999) #after it is confirmed that the code is correct and is used, the code in the db is reset to a random number for security

        

        session.flush()
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error toggling user's access statement. user: '{email}': {str(e)}")
        raise
    finally:
        session.close()
    return result

def deleteApiLogsRowsOlderThanRetentionPolicy():
    statement = delete(ApiLogs).where(ApiLogs.timestamp < (datetime.utcnow() - retention_policy))
    executeOrmStatement(statement)

def getUserStripeId(user_id):
    # print(user_id)
    statement = select(Users.stripe_id).where(Users.id == user_id)
    res = executeOrmStatement(statement)
    # print(res.first()[0])
    return res.first()[0]

def updateStripeIdForUser(user_id, stripe_id):
    statement = update(Users).where(Users.id == user_id).values(stripe_id=stripe_id)
    executeOrmStatement(statement)

def getModelFromTablename(tablename):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c