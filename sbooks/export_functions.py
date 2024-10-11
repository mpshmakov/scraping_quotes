"""Export functions for the Sbooks module.

This module provides functions to export data to CSV and JSON formats.
"""

import json

import pandas as pd
from configuration import csv_filename, json_filename, save_data_path

from .utils import create_data_folder, logger, uuid_to_str

result_csv_path = save_data_path + "/" + csv_filename + ".csv"
result_json_path = save_data_path + "/" + json_filename + ".json"


def exportToCsv(df, filename=result_csv_path):
    """
    Export a DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to export.
        filename (str, optional): The path to the output CSV file.
                                  Defaults to './data/output.csv'.
    """
    create_data_folder(filename)
    df.to_csv(filename, index=False)
    logger.info(f"Data exported to {filename}")


def exportToJson(df, filename=result_json_path):
    """
    Export a DataFrame to a JSON file, handling UUID conversion.

    Args:
        df (pandas.DataFrame): The DataFrame to export.
        filename (str, optional): The path to the output JSON file.
                                  Defaults to './data/output.json'.
    """
    create_data_folder(filename)
    # Convert DataFrame to dict, handling UUID conversion
    json_data = df.to_dict(orient="records")
    json_data = [{k: uuid_to_str(v) for k, v in record.items()} for record in json_data]

    with open(filename, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"Data exported to {filename}")
