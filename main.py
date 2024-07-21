from typing import Union

from fastapi import FastAPI, Depends

app = FastAPI()

from models import User
from sqlalchemy.orm import Session
from database import get_db

# def get_user(user_id: int, db: Session = Depends(get_db)):
#     return db.query(User).filter(User.id == user_id).first()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    # db = get_db()
    db_user = db.query(User).filter(User.id == 1).first()
    # res = get_user(user_id=1)
    print(db_user.email)
    return {"Hello": "World"}
