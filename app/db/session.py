import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
