import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PW')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    f"?sslmode={os.getenv('DB_SSL')}"
)

engine = create_engine(DATABASE_URL, echo=False)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = session()
    try:
        yield db
    finally:
        db.close()
