import os
import sys
import unittest
import uuid
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
import requests
from configuration import get_configuration
from database.operations import (
    check_tables_exist,
    initDB,
    initialize_schema,
    insert_records,
    insertRow,
)
from database.schema import TestTable, Authors, Tags, Quotes, QuotesTagsLink
from squotes import BeautifulSoup, fetchPage
from squotes.export_functions import exportMultipleDfsToOneJson, exportToCsv, exportDfToJson
from squotes.utils import clean_numeric, create_data_folder, uuid_to_str
from scripts.scraping_quotes import main, scrape_quotes
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

configuration = get_configuration()
save_data_path = configuration["save_data_path"]


# from tttt import bs, main2


class squotesFilmDataTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "test_results")
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file = open(os.path.join(self.output_dir, "test_results.txt"), "w")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.output_file.write(f"PASS: {test}\n")

    def addError(self, test, err):
        super().addError(test, err)
        self.output_file.write(f"ERROR: {test}\n{err}\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.output_file.write(f"FAIL: {test}\n{err}\n")

    def close(self):
        self.output_file.close()


class TestsquotesFunctions(unittest.TestCase):
    @patch("requests.get")
    def test_fetchPage(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        response = fetchPage("https://google.com")
        self.assertEqual(response.status_code, 200)

    @patch("requests.get")
    def test_fetchPage_exception(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        with self.assertRaises(Exception):
            fetchPage("https://google.com")


class TestExportFunctions(unittest.TestCase):
    @patch("pandas.DataFrame.to_csv")
    def test_exportToCsv(self, mock_to_csv):
        data = {
            "id": ["test-id"],
            "name": ["Test Movie"],
            "year": [2023],
            "awards": [1],
            "nominations": [3],
        }
        df = pd.DataFrame(data)
        exportToCsv(df, "test")
        filename = save_data_path + "/" + "test" + ".csv"

        mock_to_csv.assert_called_once_with(filename, index=False)

    @patch("json.dump")
    def test_exportDfToJson(self, mock_json_dump):
        data = {
            "id": ["test-id"],
            "name": ["Test Movie"],
            "year": [2023],
            "awards": [1],
            "nominations": [3],
        }
        df = pd.DataFrame(data)
        exportDfToJson(df, "test")
        mock_json_dump.assert_called_once()

    @patch("json.dump")
    def test_exportMultipleDfsToOneJson(self, mock_json_dump):
        df_arr = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]
        df_names = ["name1", "name2", "name3", "name4"]
        filename = "test"

        exportMultipleDfsToOneJson(df_arr, df_names, filename)
        mock_json_dump.assert_called_once()

class TestUtils(unittest.TestCase):
    def test_uuid_to_str(self):
        test_uuid = uuid.uuid4()
        self.assertEqual(uuid_to_str(test_uuid), str(test_uuid))
        self.assertEqual(uuid_to_str("not-a-uuid"), "not-a-uuid")

    def test_clean_numeric(self):
        self.assertEqual(clean_numeric("123"), 123)
        self.assertEqual(clean_numeric("123.45"), 123)
        self.assertEqual(clean_numeric("abc"), "abc")
        self.assertEqual(clean_numeric(456), 456)


class TestDatabaseOperations(unittest.TestCase):
    # these tests don't work for some reason. the inspector's return value isn't being changed
    # @patch("sqlalchemy.inspect")
    # def test_check_tables_exist(self, mock_inspect):
    #     mock_inspector = MagicMock()
    #     mock_inspect.return_value = mock_inspector
    #     mock_inspector.get_table_names.return_value = [
    #         "boooooks",
    #         "TestTable",
    #     ]
    #     self.assertTrue(check_tables_exist())

    # @patch('sqlalchemy.inspect')
    # def test_check_tables_not_exist(self, mock_inspect):
    #     mock_inspect.return_value.get_table_names.return_value = []
    #     self.assertFalse(check_tables_exist())

    @patch("sqlalchemy.orm.Session")
    def test_insert_records(self, mock_session):
        records = [MagicMock(), MagicMock()]
        insert_records(mock_session, records)
        mock_session.add_all.assert_called_once_with(records)
        mock_session.commit.assert_called_once()

    @patch("sqlalchemy.orm.Session")
    def test_insert_records_exception(self, mock_session):
        records = [MagicMock(), MagicMock()]
        mock_session.commit.side_effect = SQLAlchemyError()
        with self.assertRaises(SQLAlchemyError):
            insert_records(mock_session, records)

    @patch("database.operations.initialize_schema")
    @patch("database.operations.check_tables_exist")
    @patch("database.operations.Session")
    def test_initDB(
        self, mock_Session, mock_check_tables_exist, mock_initialize_schema
    ):
        mock_check_tables_exist.return_value = True
        mock_session = MagicMock()
        mock_Session.return_value = mock_session

        initDB()

        mock_initialize_schema.assert_called_once()
        mock_check_tables_exist.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("database.operations.initialize_schema")
    @patch("database.operations.check_tables_exist")
    @patch("database.operations.Session")
    def test_initDB_tables_not_exist(
        self, mock_Session, mock_check_tables_exist, mock_initialize_schema
    ):
        mock_check_tables_exist.return_value = False
        initDB()
        mock_initialize_schema.assert_called_once()
        mock_check_tables_exist.assert_called_once()
        mock_Session.assert_not_called()

    @patch("database.operations.check_tables_exist")
    @patch("database.operations.Session")
    def test_insertRow(self, mock_Session, mock_check_tables_exist):
        mock_check_tables_exist.return_value = True
        mock_session = MagicMock()
        mock_Session.return_value = mock_session

        row = MagicMock()
        row.__tablename__ = "test_table"
        insertRow(row)

        mock_session.add.assert_called_once_with(row)
        mock_session.commit.assert_called_once()

    @patch("database.operations.check_tables_exist")
    @patch("database.operations.Session")
    def test_insertRow_tables_not_exist(self, mock_Session, mock_check_tables_exist):
        mock_check_tables_exist.return_value = False
        row = MagicMock()
        insertRow(row)
        mock_Session.assert_not_called()

    @patch("database.operations.check_tables_exist")
    @patch("database.operations.Session")
    def test_insertRow_exception(self, mock_Session, mock_check_tables_exist):
        mock_check_tables_exist.return_value = True
        mock_session = MagicMock()
        mock_Session.return_value = mock_session
        mock_session.commit.side_effect = SQLAlchemyError()

        row = MagicMock()
        row.__tablename__ = "test_table"
        with self.assertRaises(SQLAlchemyError):
            insertRow(row)

    @patch("database.operations.MetaData")
    @patch("database.operations.Table")
    @patch("database.operations.engine")
    def test_initialize_schema(self, mock_engine, mock_Table, mock_MetaData):
        mock_metadata = MagicMock()
        mock_MetaData.return_value = mock_metadata

        initialize_schema()

        mock_MetaData.assert_called_once()
        self.assertEqual(mock_Table.call_count, 5)  # Called for both tables
        mock_metadata.create_all.assert_called_once_with(mock_engine)

    @patch("database.operations.MetaData")
    @patch("database.operations.engine")
    def test_initialize_schema_exception(self, mock_engine, mock_MetaData):
        mock_metadata = MagicMock()
        mock_MetaData.return_value = mock_metadata
        mock_metadata.create_all.side_effect = SQLAlchemyError()

        with self.assertRaises(SQLAlchemyError):
            initialize_schema()


class TestDatabaseSchema(unittest.TestCase):
    def test_Tags(self):
        tag = Tags("test-tag")
        self.assertEqual(tag.tag, "test-tag")

    def test_Authors(self):
        author = Authors("test-author", "Some information about the author.")
        self.assertEqual(author.author, "test-author")
        self.assertEqual(author.about, "Some information about the author.")

    def test_Quotes(self):
        id = str(uuid.uuid4())
        quote = Quotes(id, "This is a test quote.", "test-author")
        self.assertEqual(quote.id, id)
        self.assertEqual(quote.text, "This is a test quote.")
        self.assertEqual(quote.author, "test-author")

    def test_QuotesTagsLink(self):
        quote_id = str(uuid.uuid4())
        tag = "test-tag"
        quotes_tags_link = QuotesTagsLink(quote_id, tag)
        self.assertEqual(quotes_tags_link.quote_id, quote_id)
        self.assertEqual(quotes_tags_link.tag, tag)

    def test_TestTable(self):
        test_entry = TestTable("test-id", "Test Entry", 5)
        self.assertEqual(test_entry.id, "test-id")
        self.assertEqual(test_entry.text, "Test Entry")
        self.assertEqual(test_entry.numbers, 5)


    @patch("squotes.fetchPage")
    @patch("bs4.BeautifulSoup")
    def test_scraping_quotes(self, mock_bs, mock_fetchPage):
        url = configuration["url"]
        pagesnum = configuration["pagesnum"]
        quotes_pages_urls = []
        for i in range(pagesnum):
            next_page_url = url + "page/" + str(i+1)
            quotes_pages_urls.append(next_page_url)

        results = scrape_quotes(quotes_pages_urls)
        self.assertEqual(len(results[0]), 100)
        self.assertEqual(len(results[1]), 235)
        self.assertEqual(len(results[2]), 138)
        self.assertEqual(len(results[3]), 50)
        self.assertEqual(
            len(results), 4
        )  # id, title, price, availability, star_rating, category

    @patch("scripts.scraping_quotes.fetchPage")
    def test_scraping_quotes_fetch_exception(self, mock_fetchPage):
        mock_fetchPage.return_value = None
        with self.assertRaises(Exception) as context:
            scrape_quotes()
            print("context.exception in fetch_exception ", str(context.exception))
            self.assertTrue(
                "Failed to fetch the page - No internet connection."
                in str(context.exception)
            )

    @patch("scripts.scraping_quotes.bs")
    def test_scrape_quotes_page_structure_exception(self, mock_bs):
        mock_soup = BeautifulSoup(
            fetchPage("https://www.google.com/").content, features="html.parser"
        )
        mock_bs.return_value = mock_soup

        with self.assertRaises(Exception):
            scrape_quotes()

    @patch("scripts.scraping_quotes.scrape_quotes")
    @patch("scripts.scraping_quotes.initDB")
    @patch("scripts.scraping_quotes.exportToCsv")
    @patch("scripts.scraping_quotes.exportMultipleDfsToOneJson")
    def test_main(
        self,
        mock_exportMultipleDfsToOneJson,
        mock_exportToCsv,
        mock_initDB,
        mock_scrape,
    ):  
        mock_scrape.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        main()
        mock_initDB.assert_called_once()
        mock_scrape.assert_called_once()
        # self.assertEqual(mock_insertRow.call_count, 2)
        # mock_exportToCsv.assert_has_calls()
        self.assertEqual(mock_exportToCsv.call_count, 4)
        mock_exportMultipleDfsToOneJson.assert_called_once()


if __name__ == "__main__":
    unittest.main(
        testRunner=unittest.TextTestRunner(resultclass=squotesFilmDataTestResult)
    )
