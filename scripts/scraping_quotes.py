"""Books to Scrape scraper and database population script.
This script scrapes book data from the Books to Scrape website,
stores it in a database, and exports it to CSV and JSON formats.
"""

import concurrent.futures
import threading
import uuid

import pandas as pd
from bs4 import Tag
from configuration import get_configuration
from database import Books, Session, TestTable, initDB, insertRow
from database.operations import check_tables_exist, initialize_schema
from sbooks import BeautifulSoup as bs
from sbooks import fetchPage, logger, requests
from sbooks.export_functions import exportToCsv, exportToJson
from sbooks.utils import clean_numeric
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

# 1) extract links of categories
#     1. extract number of pages for this category
#       1. extract links of books
#         1. add book to the dataframe with the respective category


pbar_quotes = None


def category_worker(category):

    quotes = []

    a_tag = category.find("a")

    category_url = a_tag.get("href")
    category_name = a_tag.string.strip()
    logger.info("category name: " + category_name)

    category_page = bs(fetchPage(url + category_url).content, features="html.parser")

    num_pages = 1
    num_pages_tag = category_page.find(class_="current")

    if num_pages_tag is not None:
        logger.info("num_pages is not None")
        num_pages = int(num_pages_tag.text.split("of ", 1)[1])
    logger.info("pages: " + str(num_pages))

    new_page_url = category_url
    for i in range(num_pages):
        iterator = i + 1

        # page n is just page-n.html instead of index.html
        if iterator != 1:
            new_page_url = category_url.replace("index", "page-" + str(iterator))
        logger.info("current category page url: " + url + new_page_url)
        current_page = bs(fetchPage(url + new_page_url).content, features="html.parser")

        # get links of books
        books_tag = current_page.find("ol")
        books_a_tags = books_tag.find_all("a", title=True)

        for book_a in books_a_tags:
            book_url = book_a.get("href").split("/", 3)[3]
            logger.info("current book url: " + book_url)

            # soup of the book -> parse the details into a dict
            book_page = bs(
                fetchPage(url + "catalogue/" + book_url).content,
                features="html.parser",
            )
            main_div_tag = book_page.find(class_="col-sm-6 product_main")

            id = str(uuid.uuid4())
            logger.info("uuid: " + id)

            title = get_title(main_div_tag)
            logger.info("title: " + title)

            price = get_price(main_div_tag)
            logger.info("price: " + str(price))

            availability = get_availability(main_div_tag)
            logger.info("availability: " + str(availability))

            rating = get_rating(main_div_tag)
            logger.info("rating: " + str(rating))

            the_category = category_name
            logger.info("category: " + category_name)
            quotes.append([id, title, price, availability, rating, the_category])
            pbar_quotes.update(1)

    pbar_category.update(1)
    return quotes


def init_pbars(soup, categories_list):
    global pbar_category
    global pbar_quotes
    num_of_books = get_num_of_books(soup)
    pbar_quotes = tqdm(total=num_of_books, desc="books")
    pbar_category = tqdm(total=len(categories_list), desc="categories")


def get_num_of_books(soup: bs):
    num_of_books_str = (
        soup.find(class_="col-sm-8 col-md-9").find("form").find("strong").get_text()
    )
    return int(num_of_books_str)


# functions to get each of the books' parameters (i believe it is easier to debug and maintain the code this way because the parsing of the page may get very complicated)
def get_title(main_div_tag):
    title = main_div_tag.find("h1").text.strip()
    return title


def get_price(main_div_tag):
    price = float(main_div_tag.find(class_="price_color").text.strip().split("£", 1)[1])
    return price


def get_availability(main_div_tag):
    tmp_availability = (
        main_div_tag.find(class_="instock availability").text.strip().split("(", 1)[1]
    )
    availability = int(tmp_availability.split("available", 1)[0])
    return availability


def get_rating(main_div_tag):
    tmp_star_rating = main_div_tag.find(class_="star-rating").get("class")[1]
    star_rating = word_number_to_int(tmp_star_rating)
    return star_rating


def scrape_quotes():
    """
    Scrape books data from https://books.toscrape.com/.
    Returns:
    list: A list of tuples containing books data (id, title, how many in stock, rating, category).
    Raises:
    Exception: If the page structure has changed and data cannot be scraped.
    """

    quotes = []

    try:
        response = fetchPage(url)
        if response is None:
            raise Exception("Failed to fetch the Quotes page")

        quote_page = bs(response.content, features="html.parser")
        logger.info("Created the soup.")

        quotes_pages = []

        while True:
            quotes_pages.append(quote_page)
            next_page = quote_page.find(class_="col-md-8").find("nav").find("a")["href"]
            

        # init_pbars(soup, categories_list)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            quotes_map = executor.map(category_worker, categories_list)
            logger.debug("max workers: " + str(executor._max_workers))
        pbar_category.close()

        for book in quotes_map:
            if book != None:
                for j in range(len(book)):
                    quotes.append(book[j])

        return quotes
    except Exception as e:
        logger.error(f"Error scraping quotes: {str(e)}")
        raise


def main():
    """
    Main function to orchestrate the scraping, database population, and data export process.
    """
    try:
        # Initialize the database schema
        initialize_schema()
        # Verify tables exist
        if not check_tables_exist():
            logger.error("Tables do not exist after schema initialization. Exiting.")
            return

        quotes_data = scrape_quotes()

        # Create AcademyAwardWinningFilms objects
        quotes = [Books(*book) for book in quotes_data]

        # Initialize the database and insert all movies
        initDB(quotes)

        # Verify tables exist again
        if not check_tables_exist():
            logger.error("Tables do not exist after initDB. Exiting.")
            return

        # Test inserting individual rows
        new_quotes = Books(str(uuid.uuid4()), "Test Book", 22.0, 1, 5, "category")
        new_test = TestTable(1, 43, 6)

        insertRow(new_quotes)
        # print("Inserted new film.")
        insertRow(new_test)

        # another_test = TestTable(2, 'text', 1.1)
        # insertRow(another_test)
        # print("Inserted test entry.")

        # Create DataFrame for CSV and JSON export
        df = pd.DataFrame(
            quotes_data,
            columns=["id", "title", "price", "availability", "star_rating", "category"],
        )
        exportToCsv(df)
        exportToJson(df)

    except SQLAlchemyError as e:
        logger.error(f"A database error occurred: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
