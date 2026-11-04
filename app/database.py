import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_username", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_host", "localhost"),
    port=int(os.getenv("DB_port", "5432")),
    database=os.getenv("DB_name", "factorymind")
)

engine = create_engine(db_url)

# creating session to connect to the DB using python objects
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# This generator will later be used with FastAPI's Depends() so each API request gets a database session that is properly closed.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
