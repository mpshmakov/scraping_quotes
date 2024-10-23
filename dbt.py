from database import initDB, insertRow, Tags
from database.operations import initialize_schema

initialize_schema()

initDB()

tag_row = Tags(tag="a;ldsjf;lsakjdf")
insertRow(tag_row)