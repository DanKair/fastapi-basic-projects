from models.users import Base

from .config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.db_url, echo=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(engine)      