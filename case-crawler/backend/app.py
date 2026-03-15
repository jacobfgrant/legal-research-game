"""Case Crawler — FastAPI backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Case Crawler API", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}
