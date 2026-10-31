from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from models import Todos, Users
from typing import Annotated, Optional
from database import engine, SessionLocal
from router import auth, admin
from router.auth import get_current_user
from router.auth import bcrypt_context


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)

class Todo(BaseModel):
    title: str
    description: str=Field(max_length=300, example="Milk, Bread, Eggs")
    priority: int=Field(lt=6, gt=0, example=3)
    completed: bool

class TodoUpdate(BaseModel):
    title: Optional[str]=Field(default=None)
    description: Optional[str]=Field(default= None,max_length=300, example="Milk, Bread, Eggs")
    priority: Optional[int]=Field(default=None, lt=6, gt=0, example=3)
    completed: Optional[bool]=Field(default=None)

class UpdateUsers(BaseModel):
    email: Optional[str]=Field(default=None)
    firstname: Optional[str]=Field(default=None)
    lastname: Optional[str]=Field(default=None)
    phone_number: Optional[str]=Field(default=None, max_length=11, example="01234567890")

class updatePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/")
def read_totos(user:user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    todos = db.query(Todos).filter(Todos.owner_id==user.get('id')).all()
    
    return todos

@app.get("/todo/{todo_id}")
def read_specific_totos(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    specific_todo = db.query(Todos).filter(Todos.owner_id==user.get('id')).filter(Todos.id == todo_id).first()
    
    if specific_todo is not None:
        return specific_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/create/")
def create_todo(user: user_dependency,db: db_dependency, new_todo: Todo):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    todo_model = Todos(**new_todo.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()
    
    return JSONResponse(status_code=201, content={"message": "Todo created successfully"})

@app.put("/edit/{todo_id}")
def update_todo(user: user_dependency, db: db_dependency, todo_id: int, update_todo: TodoUpdate):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    todo = db.query(Todos).filter(Todos.owner_id==user.get('id')).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    update_data =update_todo.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(todo, key, value)
    
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "Todo updated successfully"})
    
@app.delete("/delete/{todo_id}")
def delete_todo(user: user_dependency,db: db_dependency, todo_id: int):
    todo = db.query(Todos).filter(Todos.owner_id==user.get('id')).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todos).filter(Todos.owner_id==user.get('id')).filter(Todos.id == todo_id).delete()
        
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "Todo deleted successfully"})
    
@app.get("/user_profile")
def get_user(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_profile_data = db.query(Users).filter(Users.id==user.get('id')).first()
    
    return user_profile_data

@app.put("/edit_profile")
def editProfile(user: user_dependency, db: db_dependency, updateUser: UpdateUsers):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.query(Users).filter(Users.id==user.get('id')).first()
    
    user_data = updateUser.model_dump(exclude_unset=True)
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "User updated successfully"})

@app.put("/password_update")
def updatePassword(user: user_dependency, db: db_dependency, update_password: updatePassword):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.query(Users).filter(Users.id==user.get('id')).first()
    
    if not bcrypt_context.verify(update_password.current_password, user.hash_password):
        raise HTTPException(status_code=400, detail="Wrong Password")
    
    if update_password.new_password != update_password.confirm_password:
        raise HTTPException(status_code=400, detail="Password does not match")
    
    user.hash_password = bcrypt_context.hash(update_password.new_password)
    db.add(user)
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "Password updated successfully"})