import mysql.connector
from mysql.connector import Error
from core.config import settings
import os

def get_db():
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            port=settings.DB_PORT
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)