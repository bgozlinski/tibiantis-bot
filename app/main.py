import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import character

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("FastAPI application starting up")
    yield
    logger.info("FastAPI application shutting down")

app = FastAPI(lifespan=lifespan)
logger.info("Registering API routes")

@app.get("/")
async def index():
    logger.debug("Health check endpoint called")
    return {"ping": "pong"}
app.include_router(character.router, prefix="/character", tags=["Characters"])
