
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
import argparse

def get_configuration() -> json:
    # Open and read the JSON file
    with open('configuration.json', 'r') as file:
        configuration = json.load(file)

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url', type=str, help='modify page url. url must have "/" in the end.')
    parser.add_argument('--save_data_path', dest='save_data_path', type=str, help="path where the output files are saved (i.e json, csv output). The path must have '/' in the end.")
    parser.add_argument('--json_filename', dest='json_filename', type=str, help="json output filename. specify only the filename without '.json' in the end.")
    parser.add_argument('--db_name', dest='db_name', type=str, help="path where log files are saved. The path must have '/' in the end.")
    parser.add_argument('--db_username', dest='db_username', type=str)
    parser.add_argument('--db_password', dest='db_password', type=str)
    parser.add_argument('--db_ip', dest='db_ip', type=str)
    parser.add_argument('--db_port', dest='db_port', type=str)
    parser.add_argument('--db_enable', dest='db_enable', type=int)

    
    args = parser.parse_args()

    for arg, value in vars(args).items():
        if value is not None:
            configuration[arg] = value
        # print(arg, value)



    return configuration
