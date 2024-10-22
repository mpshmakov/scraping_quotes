"""Database schema module.

This module defines the SQLAlchemy ORM models for the database tables.
"""

from sqlalchemy import DECIMAL, CheckConstraint, Column, Integer, String, TEXT, ForeignKey
from sqlalchemy.orm import declarative_base, validates

Base = declarative_base()

class Tags(Base):

    __tablename__ = "tags"

    tag = Column(String(100), primary_key=True)

    def __init__(self, tag: str):
        self.tag = tag

class Authors(Base):

    __tablename__ = "authors"

    author = Column(String(100), primary_key=True)
    about = Column(TEXT)

    def __init__(self, author: str, about: str):
        self.author = author
        self.about = about



class Quotes(Base):
    """
    SQLAlchemy ORM model for the quotes table.
    """

    __tablename__ = "quotes"

    id = Column(String(36), primary_key=True)
    text = Column(String(255), nullable=False)
    author = Column(String(100), ForeignKey('authors.author'))

    @validates("id")
    def validate_id(self, key, value):
        if len(value) != 36:
            raise Exception("uuid field doesn't have 36 characters.")
        return value

    def __init__(
        self,
        id: str,
        text: str,
        author: float,
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

    quote_id = Column(String(36), ForeignKey('quotes.id'))
    tag = Column(String(100), ForeignKey('tags.tag'))

    def __init__(self, quote_id: str, tag: str):
        self.quote_id = quote_id
        self.tag = tag
        

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
