# routers/user.py

from fastapi import APIRouter, HTTPException, Depends
from core.database import get_db
from core.models import UserCreate, UserLogin, UserOut
from typing import List
import mysql.connector

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        cursor.execute(
            "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (user.name, user.email, user.password, user.role)
        )
        db.commit()
        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.post("/login", response_model=UserOut)
def login_user(user: UserLogin, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM Users WHERE email = %s AND password = %s",
            (user.email, user.password)
        )
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return result
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/", response_model=List[UserOut])
def get_all_users(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, email, role FROM Users")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
