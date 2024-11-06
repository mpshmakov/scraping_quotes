# from database import initDB, insertRow, Tags
# from database.operations import initialize_schema

# # initialize_schema()

# initDB()

# tag_row = Tags(tag="a;ldsjf;lsakjdf")
# insertRow(tag_row)

# from time import sleep
# from tqdm import tqdm

# pbar = tqdm(total=100, desc="skssk")

# # pbar.update(10)
# # pbar.update(10)
# # pbar.update(10)
# # pbar.reset()
# # pbar.update(n=10)

# for i in range(100):
#     pbar.reset()
#     pbar.update(i)
#     pbar.refresh()
#     sleep(1)

import argparse

def rate():
    parser = argparse.ArgumentParser()
    parser.add_argument('--product_id', dest='product_id', type=str, help='Add product_id')
    parser.add_argument('--smth', dest='smth', type=str)
    args = parser.parse_args()

    for arg, value in vars(args).items():
        print(arg, value)
    # print (args.product_id)