
import json


url = str()
pagesnum = str()

save_data_path = str()

logs_path = str()
db_path = str()

csv_filename = str()
json_filename = str()
db_filename = str()


def init_configuration():

    global url, pagesnum, save_data_path, logs_path, db_path, csv_filename, json_filename, db_filename

    # Open and read the JSON file
    with open('configuration.json', 'r') as file:
        data = json.load(file)

    url = data["url"]
    pagesnum = data["pagesnum"]

    save_data_path = data["save_data_path"]

    logs_path = data["logs_path"]
    db_path = data["db_path"]

    csv_filename = data["csv_filename"]
    json_filename = data["json_filename"]
    db_filename = data["db_filename"]
