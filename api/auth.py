from datetime import timedelta, datetime
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from starlette import status
from database.operations import executeOrmStatement, initDB, insertRow
from database.schema import Authors,Tags,Quotes,QuotesTagsLink,Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from secret import SECRET_KEY, ENCODING_ALG as ALGORITHM

initDB(truncate=True)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# SECRET_KEY = "smth"
# ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    create_user_model = Users(id=str(uuid.uuid4()), username=create_user_request.username, password=bcrypt_context.hash(create_user_request.password))
    insertRow(create_user_model)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.Users.username, user.Users.id, timedelta(minutes=20))

    return {"access_token" : token, "token_type" : "bearer"}

def authenticate_user(username:str, password:str):
    user = executeOrmStatement(select(Users).filter(Users.username == username)).first()
    print(user)
    if not user:
        return False
    if not bcrypt_context.verify(password, user.Users.password):
        print(bcrypt_context.verify(password, user.Users.password))
        return False
    return user

def create_access_token(username: str, id: str, expires_delta: timedelta):
    encode = {'sub':username , 'id': id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username' : username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
