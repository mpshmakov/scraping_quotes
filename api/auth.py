import asyncio
from datetime import timedelta, datetime
from typing import Annotated, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from email_validator import EmailNotValidError, validate_email
import httpx
from sqlalchemy import select
from starlette import status
from database.operations import authenticateConfirmCodeAndResetIt, changeUserPassword, executeOrmStatement, generateAndUpdateConfirmCodeForUser, generateAndUpdateUserPassword, initDB, insertRow
from database.schema import Authors,Tags,Quotes,QuotesTagsLink,Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from secret import SECRET_KEY, ENCODING_ALG as ALGORITHM
from notifications import email
from database.apilogclass import log
from . import domain, port


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

def email_val(email):
    try:
        em = validate_email(email)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email address not supported or the value is not an email.')
    finally:
        return em.normalized

class CreateUserRequest(BaseModel):
    email:str
    fullname: str
    password:str

    @validator('email')
    def validate_emailll(cls, value):
        return email_val(value)

class Token(BaseModel):
    access_token: str
    token_type: str

class createToken(BaseModel):
    email:str
    id:str
    access:int

class changePassword(BaseModel):
    current:str
    new:str

class requestCode(BaseModel):
    email:str

    @validator('email')
    def validate_emailll(cls, value):
        email_val(value)

class resetPassword(BaseModel):
    email:str
    code:int

    @validator('email')
    def validate_emailll(cls, value):
        email_val(value)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    print("req email", create_user_request.email)
    user = executeOrmStatement(select(Users).filter(Users.email == create_user_request.email)).first()
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This email is already taken.')

    id = str(uuid.uuid4())
    create_user_model = Users(id=id, stripe_id=None, email=create_user_request.email, fullname=create_user_request.fullname, password=bcrypt_context.hash(create_user_request.password), access=0)
    insertRow(create_user_model)

    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post(domain + '/auth/token', json={"email": create_user_request.email, "id": id, "access": 0})
        print("res", res.json())
        log.info(create_user_request.email, "User registered.")
        asyncio.create_task(email.register_notifications(create_user_request.email))
        return res.json()

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestJSON):
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    
    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post(domain + '/auth/token', json={"email": user.Users.email, "id": user.Users.id, "access": user.Users.access})
        print("res", res.json())
        print(user.Users.email)
        log.info(str(user.Users.email), "User login.")
        asyncio.create_task(email.login_notifications(form_data.email))
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

    
@router.post("/change_password")
async def change_password(user: Annotated[dict, Depends(get_current_user)], password: changePassword):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    print(password)

    if password.current == password.new:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password can't be the same as the current one.") 

    try:
        changeUserPassword(user["id"], bcrypt_context.hash(password.new), password.current)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password doesn't match.")

    async with httpx.AsyncClient() as client:
        print('before res')
        res = await client.post(domain + '/auth/token', json={"email": user['email'], "id": user['id'], "access": user['access']})
        print("res", res.json())
        print(user['email'])
        log.info(str(user['email']), "User login.")
        asyncio.create_task(email.change_password_notifications(user['email']))
        return res.json()
    
@router.post("/password_reset")
async def generate_new_password(body:resetPassword):
    auth = authenticateConfirmCodeAndResetIt(email=body.email, code=body.code)
    if auth is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code doesn't match.")

    password = None
    try:
        password = generateAndUpdateUserPassword(body.email)
        asyncio.create_task(email.send_new_password(body.email, password))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password doesn't match.")
    
    return {"new_password": password}

    
@router.post("/request_code")
async def request_code(body: requestCode):
    try:
        await email.send_password_reset_code(body.email)
    except ValueError :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with the email {email.email} doesn't exist.")
    return {"msg":"The code has been sent to your email. Send the code with your email address to /auth/password_reset endpoint."}