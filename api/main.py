from datetime import timedelta
import json
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
import httpx
from starlette import status
import requests


from pydantic import BaseModel
from sqlalchemy import select, update
import uvicorn
from api import auth
from configuration import get_configuration
from database.operations import executeOrmStatement, getModelFromTablename, toggleAccessForUser
from database.schema import Authors, Quotes, Tags, QuotesTagsLink, Users
from fastapi.security import OAuth2PasswordBearer
from database.apilogclass import log

app = FastAPI()
app.include_router(auth.router)
user_dependency = Annotated[dict, Depends(auth.get_current_user)]

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}

def check_auth_and_access(user):
    print("check",user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed.')
    if user['access'] == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access check failed.")

@app.patch("/user/toggle_access")
async def toggle_current_user_access(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed.')    
    print(user)
    access = toggleAccessForUser(user['id'])
    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post('http://127.0.0.1:8000/auth/token', json={"username":user['username'], "id":user['id'], "access":access})
        print("res", res.json())
        res = res.json()
        res["access"] = access
        log.info(user['username'], f"Set user's access to {access}")
        return res

    

@app.get("/")
def root(user: user_dependency):
    check_auth_and_access(user)
    return {"User": user}

# get data from db
# @app.get("/{table}")
# def get_quotes(table: str):
#     model = getModelFromTablename(table)
#     res = executeOrmStatement(select(model))
#     # quotes = []
#     # for quote in res.all():
#     #     quotes.append({"quote_uuid" : quote.Quotes.id, "quote_text" :quote.Quotes.text, "quote_author" :quote.Quotes.author})

    # return quotes

@app.get("/quotes")
def get_quotes(user: user_dependency):
    print(user)
    check_auth_and_access(user)
    res = executeOrmStatement(select(Quotes))
    quotes = []
    for quote in res.all():
        quotes.append({"quote_uuid" : quote.Quotes.id, "quote_text" :quote.Quotes.text, "quote_author" :quote.Quotes.author})
    log.info(user['username'], "Retrieved quotes.")
    return quotes

@app.get("/tags")
def get_tags(user: user_dependency):
    check_auth_and_access(user)
    res = executeOrmStatement(select(Tags))
    tags = []
    for tag in res.all():
        tags.append({"0" : tag.Tags.tag}) # matching how to_dict converts dataframe to dict
    log.info(user['username'], "Retrieved tags.")    
    return tags

@app.get("/quotes_tags_link")
def get_quotes_tags_link(user: user_dependency):
    check_auth_and_access(user)
    res = executeOrmStatement(select(QuotesTagsLink))
    quotes_tags_link = []
    for link in res.all():
        quotes_tags_link.append({"quote_uuid" : link.QuotesTagsLink.quote_id, "tag" : link.QuotesTagsLink.tag}) # matching how to_dict converts dataframe to dict
    log.info(user['username'], "Retrieved quotes_tags_link.")
    return quotes_tags_link

@app.get("/authors")
def get_authors(user: user_dependency):
    check_auth_and_access(user)
    res = executeOrmStatement(select(Authors))
    authors = []
    for author in res.all():
        authors.append({"author" : author.Authors.author, "about" : author.Authors.about}) 
    log.info(user['username'], "Retrieved authors.")
    return authors




# get data from json

# @app.get("/quotes")
# def get_quotes():
#     json_filename, json_path = get_configuration(["json_filename", "save_data_path"])
#     with open(f'{json_path}/{json_filename}.json', 'r') as file:
#         data = json.load(file)

#     return data["quotes"]


if __name__ == "__main__":
    uvicorn.run(app)