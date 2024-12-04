from database.schema import ApiLogs
from uuid import uuid4
from database.operations import insertRow

class apilog:
    def info(self, username:str, message:str):
        insertRow(ApiLogs(str(uuid4()), username, "info", message))
    
    def warning(self, username:str, message:str):
        insertRow(ApiLogs(str(uuid4()), username, "warning", message))

    def error(self, username:str, message:str):
        insertRow(ApiLogs(str(uuid4()), username, "error", message))

log = apilog()