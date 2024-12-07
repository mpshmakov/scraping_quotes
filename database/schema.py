"""Database schema module.

This module defines the SQLAlchemy ORM models for the database tables.
"""

from datetime import datetime
from sqlalchemy import DECIMAL, CheckConstraint, Column, DateTime, Integer, String, TEXT, ForeignKey, Date, func
from sqlalchemy.orm import declarative_base, validates, relationship

Base = declarative_base()

class Tags(Base):

    __tablename__ = "tags"

    tag = Column(String(100), primary_key=True)

    quotes_tags_link = relationship("QuotesTagsLink", back_populates="tags")

    def __init__(self, tag: str):
        self.tag = tag

class Authors(Base):

    __tablename__ = "authors"

    author = Column(String(100), primary_key=True)
    about = Column(TEXT)

    quotes = relationship("Quotes", back_populates="authors")

    def __init__(self, author: str, about: str):
        self.author = author
        self.about = about



class Quotes(Base):
    """
    SQLAlchemy ORM model for the quotes table.
    """

    __tablename__ = "quotes"

    id = Column(String(36), primary_key=True)
    text = Column(TEXT, nullable=False)
    author = Column(String(100), ForeignKey('authors.author'))

    authors = relationship("Authors", back_populates="quotes")
    quotes_tags_link = relationship("QuotesTagsLink", back_populates="quotes")

    @validates("id")
    def validate_id(self, key, value):
        if len(value) != 36:
            raise Exception("uuid field doesn't have 36 characters.")
        return value

    def __init__(
        self,
        id: str,
        text: str,
        author: str,
    ):
        """
        Initialize a Books instance.

        Args:
            id (str): Unique identifier for the book.
            title (str): Title of the book.
            price (float): Price of the book.
            availability (int): Number of copies available.
            star_rating (int, optional): Star rating of the book (0 to 5).
            category (str): Category of the book.
        """
        self.id = id
        self.text = text
        self.author = author

class QuotesTagsLink(Base):

    __tablename__ = "quotes_tags_link"

    quote_id = Column(String(36), ForeignKey('quotes.id'), primary_key=True)
    tag = Column(String(100), ForeignKey('tags.tag'), primary_key=True)

    quotes = relationship("Quotes", back_populates="quotes_tags_link")
    tags = relationship("Tags", back_populates="quotes_tags_link")


    def __init__(self, quote_id: str, tag: str):
        self.quote_id = quote_id
        self.tag = tag

class Users(Base):

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    stripe_id = Column(String(150), unique=True, nullable=True)
    email = Column(String(30), unique=True)
    fullname = Column(String(100))
    password = Column(TEXT, nullable=False)
    access = Column(Integer, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    apilogs = relationship("ApiLogs", back_populates='users')
    confirm_codes = relationship("ConfirmationCodes", back_populates='users')


    def __init__(self, id:str, stripe_id, email:str, fullname:str, password:str, access:int):
        self.id = id
        self.stripe_id = stripe_id
        self.email = email
        self.fullname = fullname
        self.password = password   
        assert access >= 0 and access <= 1, "Access must be either 0 or 1."
        self.access = access 

class ApiLogs(Base):

    __tablename__ = "apilogs"

    id = Column(String(36), primary_key=True)
    email = Column(String(30), ForeignKey('users.email'))
    tag = Column(String(20), nullable=False)
    message = Column(TEXT, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("Users", back_populates='apilogs')

    def __init__(self, id:str, email:str, tag:str, message:str):
        self.id = id
        self.email = email
        print("inside class", email)
        self.tag = tag
        self.message = message

class ConfirmationCodes(Base):

    __tablename__ = "confirm_codes"

    email = Column(String(30), ForeignKey('users.email'), primary_key=True)
    code = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())

    users = relationship("Users", back_populates='confirm_codes')

    def __init__(self, email:str, code:int):
        self.email = email
        self.code = code


class TestTable(Base):
    """
    SQLAlchemy ORM model for the TestTable.
    """

    __tablename__ = "TestTable"

    id = Column(String(36), primary_key=True)
    text = Column(String(255), nullable=False)
    numbers = Column(Integer, nullable=False)

    @validates("numbers")
    def validate_numbers(self, key, value):
        # print("numbers", type(value))
        if type(value) != int:
            raise Exception("Numbers field isn't Integer.")

        return value

    def __init__(self, id: str, text: str, numbers: int):
        """
        Initialize a TestTable instance.

        Args:
            id (str): Unique identifier for the test entry.
            text (str): Text content for the test entry.
            numbers (int): Any integer.
        """
        self.id = id
        self.text = text
        self.numbers = numbers
