"""Database schema module.

This module defines the SQLAlchemy ORM models for the database tables.
"""

from sqlalchemy import DECIMAL, CheckConstraint, Column, Integer, String
from sqlalchemy.orm import declarative_base, validates

Base = declarative_base()


class Books(Base):
    """
    SQLAlchemy ORM model for the books table.
    """

    __tablename__ = "books"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    availability = Column(Integer, nullable=False)
    star_rating = Column(Integer, nullable=True)
    category = Column(String(70), nullable=False)

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price"),
        CheckConstraint("availability >= 0", name="check_availability"),
        CheckConstraint(
            "star_rating >= 0 AND star_rating <= 5", name="check_star_rating"
        ),
    )

    @validates("id")
    def validate_id(self, key, value):
        if len(value) != 36:
            raise Exception("uuid field doesn't have 36 characters.")
        return value

    @validates("availability")
    def validate_availability(self, key, value):
        # print("availability", type(value))
        if type(value) != int:
            print(type(value))
            raise Exception("availability field isn't Integer.")
        return value

    @validates("star_rating")
    def validate_star_rating(self, key, value):
        # print("star rating", type(value))
        if type(value) != int:
            raise Exception("star_rating field isn't Integer.")
        return value

    @validates("price")
    def validate_price(self, key, value):
        # print("price", type(value))
        if type(value) != float:
            raise Exception("price field isn't float.")
        return value

    def __init__(
        self,
        id: str,
        title: str,
        price: float,
        availability: int,
        star_rating: int,
        category: str,
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
        self.title = title
        self.price = price
        self.availability = availability
        self.star_rating = star_rating
        self.category = category


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
