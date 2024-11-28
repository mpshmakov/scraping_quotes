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
from database.apilogclass import log

class OAuth2PasswordRequestJSON(BaseModel):
    email: str
    password: str


initDB(truncate=False)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    email:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

class createToken(BaseModel):
    email:str
    id:str
    access:int

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    user = executeOrmStatement(select(Users).filter(Users.email == create_user_request.email)).first()
    if user is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='This email is already taken.')

    id = str(uuid.uuid4())
    create_user_model = Users(id=id, email=create_user_request.email, password=bcrypt_context.hash(create_user_request.password), access=0)
    insertRow(create_user_model)

    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post('http://127.0.0.1:8000/auth/token', json={"email": create_user_request.email, "id": id, "access": 0})
        print("res", res.json())
        log.info(create_user_request.email, "User registered.")
        email.registration_email_notification(create_user_request.email)
        return res.json()

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestJSON):
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    
    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post('http://127.0.0.1:8000/auth/token', json={"email": user.Users.email, "id": user.Users.id, "access": user.Users.access})
        print("res", res.json())
        print(user.Users.email)
        log.info(str(user.Users.email), "User login.")
        email.login_email_notification(form_data.email)
        return res.json()
    

@router.post("/token", response_model=Token)
async def generate_token(user: createToken):
    print("token")
    token = create_access_token(user.email, user.id, user.access, timedelta(minutes=20))

    return {"access_token" : token, "token_type" : "bearer"}


def authenticate_user(email:str, password:str):
    user = executeOrmStatement(select(Users).filter(Users.email == email)).first()
    print("user", user)
    if not user:
        return False
    if not bcrypt_context.verify(password, user.Users.password):
        print(bcrypt_context.verify(password, user.Users.password))
        return False
    return user

def create_access_token(email: str, id: str, access: int, expires_delta: timedelta):
    encode = {'sub':email , 'id': id, 'access': access}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    print("getcurrentuser")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        access = payload.get('access')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'email' : email, 'id': user_id, 'access': access}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
