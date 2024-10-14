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
    # headers = {
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
    #    'Accept-Language': 'en-US,en;q=0.5',
    #    'Accept-Encoding': 'gzip, deflate, br',
    #    'DNT': '1',
    #    'Connection': 'keep-alive',
    #    'Upgrade-Insecure-Requests': '1'
    # }

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
