# from database import initDB, insertRow, Tags
# from database.operations import initialize_schema

# # initialize_schema()

# initDB()

# tag_row = Tags(tag="a;ldsjf;lsakjdf")
# insertRow(tag_row)

from time import sleep
from tqdm import tqdm

pbar = tqdm(total=100, desc="skssk")

# pbar.update(10)
# pbar.update(10)
# pbar.update(10)
# pbar.reset()
# pbar.update(n=10)

for i in range(100):
    pbar.reset()
    pbar.update(i)
    pbar.refresh()
    sleep(1)
