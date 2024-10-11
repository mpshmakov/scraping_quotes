"""SBooks module initialization.

This module sets up logging and imports necessary components for web scraping
and data processing operations.
"""

import json

# Standard library imports
import os
import uuid

# Third-party imports
import pandas as pd
import requests
from bs4 import BeautifulSoup

from .export_functions import exportToCsv, exportToJson

# Local imports
from .utils import create_data_folder, logger, uuid_to_str


def fetchPage(url):
    """
    Fetch a web page and return the response.

    Args:
        url (str): The URL of the page to fetch.

    Returns:
        requests.Response: The response object from the request.

    Raises:
        Exception: If the page cannot be fetched due to network issues.
    """
    try:
        res = requests.get(url)
        logger.info("Successfully fetched the page")
        return res
    except requests.RequestException:
        logger.error("Failed to fetch the page - No internet connection.")
        raise Exception("Failed to fetch the page - No internet connection.")


# Expose commonly used functions and classes
__all__ = [
    "pd",
    "BeautifulSoup",
    "requests",
    "uuid",
    "exportToCsv",
    "exportToJson",
    "create_data_folder",
    "uuid_to_str",
    "fetchPage",
    "logger",
]
