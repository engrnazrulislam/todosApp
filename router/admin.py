from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from database import SessionLocal
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from router.auth import get_current_user
from models import Todos
router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/admin/todos")
def read_all_todos(user:user_dependency,db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication required or it is not an admin user")

    todos = db.query(Todos).all()
    
    return todos


@router.delete("/admin/delete/{todo_id}")
def delete_todo_by_admin(user: user_dependency,db: db_dependency, todo_id: int):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None or user.get('role') != 'admin':
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
        
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "Todo deleted successfully"})

@router.delete("/admin/delete_user/{user_id}")
def delete_user_by_admin(user: user_dependency,db: db_dependency, user_id: int):
    user = db.query(Users).filter(Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Users).filter(Users.id==user_id).delete()  
    db.commit()
    return JSONResponse(status_code=200, content={"message": "User deleted successfully"})