from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Using an in-memory SQLite database for this example.
# To use a file-based database, change the URL to: "sqlite:///nomad_travel.db"
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal is the factory for creating new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    """
    Creates the database and all tables defined in the models.
    """
    print("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    print("Database and tables created.")
