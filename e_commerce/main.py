from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from core.database import engine
from api import users, auth

# CRITICAL: Import your models HERE so SQLAlchemy registers them
import models
from models.users import Base  # Or: from models import User, RefreshToken

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app starts
    # Use run_in_executor if engine is synchronous, or create_all directly
    Base.metadata.create_all(bind=engine)
    yield
    # This runs when the app shuts down (clean up if needed)

app = FastAPI(name="User AUTH", lifespan=lifespan)


app.include_router(users.router)
app.include_router(auth.router)