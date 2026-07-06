from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/reconhive")

engine = create_engine(DATABASE_URL, echo=os.environ.get("SQL_ECHO", "false").lower() == "true")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
