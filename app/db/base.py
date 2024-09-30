import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = f"mysql+mysqldb://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}"
print(f"Database URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

def crear_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
