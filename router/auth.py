from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "3bf3d547badf3c46a2552029754b950754409a2eb9167e13acf1658b2c16e520"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class Create_Users(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    password: str
    role: str
    phone_number: str


    
#Authentication Function
def authenticate_user(username, password, db):
    user = db.query(Users).filter(username==Users.username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password, user.hash_password):
        return user
    return False

# Access Token for user login
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        role = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {'username': username, 'id': user_id, 'role': role}
    except:
        raise JWTError(status_code=401, detail="Invalid Token")

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/auth')
def authentication():
    return {"user": "Authenticated"}


@router.post('/createuser')
def create_user(db:db_dependency, new_user: Create_Users):
    user_model=Users(email=new_user.email,
    username=new_user.username,
    firstname=new_user.firstname,
    lastname=new_user.lastname,
    hash_password=bcrypt_context.hash(new_user.password),
    is_active=True,
    role=new_user.role,
    phone_number=new_user.phone_number
    )
    db.add(user_model)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@router.post('/login')
def login_user(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Failed Authentication"
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}

