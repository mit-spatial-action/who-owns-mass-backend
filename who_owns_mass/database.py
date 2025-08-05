# setting up database connection and session

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from who_owns_mass_fastapi.models import Base

load_dotenv()

def clean_env(key):
    value = os.getenv(key)
    return value.strip("'\"") if value else None

DB_NAME = clean_env("DB_NAME")
DB_USER = clean_env("DB_USER")
DB_PW = clean_env("DB_PW")
DB_HOST = clean_env("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SSL = clean_env("DB_SSL")

DATABASE_URL = (f"postgresql+psycopg2://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                f"?sslmode={DB_SSL}")

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
