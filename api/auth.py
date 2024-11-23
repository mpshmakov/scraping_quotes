from datetime import timedelta, datetime
from typing import Annotated, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
import httpx
from sqlalchemy import select
from starlette import status
from database.operations import executeOrmStatement, initDB, insertRow
from database.schema import Authors,Tags,Quotes,QuotesTagsLink,Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from secret import SECRET_KEY, ENCODING_ALG as ALGORITHM
from notifications import email

class OAuth2PasswordRequestJSON(BaseModel):
    # grant_type: str
    username: str
    password: str
    # client_id: Optional[str] 
    # client_secret: Optional[str] 


initDB(truncate=False)

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

class createToken(BaseModel):
    username:str
    id:str
    access:int

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    create_user_model = Users(id=str(uuid.uuid4()), username=create_user_request.username, password=bcrypt_context.hash(create_user_request.password), access=0)
    insertRow(create_user_model)
    return {"username":create_user_model.username, "id":create_user_model.id, "access":0}

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestJSON):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    
    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post('http://127.0.0.1:8000/auth/token', json={"username": user.Users.username, "id": user.Users.id, "access": user.Users.access})
        print("res", res.json())
        email.login_email_notification(form_data.username)
        return res.json()
    

@router.post("/token", response_model=Token)
async def generate_token(user: createToken):
    print("token")
    token = create_access_token(user.username, user.id, user.access, timedelta(minutes=20))

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

def create_access_token(username: str, id: str, access: int, expires_delta: timedelta):
    encode = {'sub':username , 'id': id, 'access': access}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    print("getcurrentuser")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        access = payload.get('access')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username' : username, 'id': user_id, 'access': access}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
