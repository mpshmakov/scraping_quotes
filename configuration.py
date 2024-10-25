
# TODO: could be remade as a class with constructor which automatically inits the conf variables inside the class 
# (i guess class would be better in case more functions for configuration will be added in the future. otherwise i see no difference)

import json

# url = str()
# pagesnum = str()

# save_data_path = str()

# logs_path = str()
# db_path = str()

# csv_filename = str()
# json_filename = str()
# db_filename = str()


def get_configuration() -> json:

    # global url, pagesnum, save_data_path, logs_path, db_path, csv_filename, json_filename, db_filename

    # Open and read the JSON file
    with open('configuration.json', 'r') as file:
        configuration = json.load(file)

    return configuration
    # url = configuration["url"]
    # print("url", url)
    # print("data[url]", configuration["url"])
    # pagesnum = configuration["pagesnum"]

    # save_data_path = configuration["save_data_path"]

    # logs_path = configuration["logs_path"]
    # db_path = configuration["db_path"]

    # csv_filename = configuration["csv_filename"]
    # json_filename = configuration["json_filename"]
    # db_filename = configuration["db_filename"]
