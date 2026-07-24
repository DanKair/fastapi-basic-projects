from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from core.database import Base, engine
from core.redis import ip_redis
from core.config import settings
from api import products, users, auth, admin, categories

# CRITICAL: Import your models HERE so SQLAlchemy registers them
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app starts
    # Use run_in_executor if engine is synchronous, or create_all directly
    engine.echo = settings.DEBUG_ENABLED # Controls SQL Logging (DDL)
    Base.metadata.create_all(bind=engine)
    yield
    # This runs when the app shuts down (clean up if needed)

app = FastAPI(name="User AUTH", lifespan=lifespan, debug=settings.DEBUG_ENABLED)
UPLOAD_DIRECTORY = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIRECTORY.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIRECTORY), name="uploads")

@app.middleware("http")
def ip_blacklist_middleware(request: Request, call_next):
    # Direct client IP since there is no reverse proxy
    client_ip = request.client.host

    # Check Database 1 for the IP
    if ip_redis.exists(client_ip):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access denied: Your IP address is blocked."}
        )

    return call_next(request)

@app.get("/")
def health_check():
    return {"health_status": "ok"}

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(categories.router)
