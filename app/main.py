import logging
from fastapi import FastAPI
from app.api import character

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def index():
    logger.debug("Health check endpoint called")
    return {"ping": "pong"}


@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down")


# Include routers
logger.info("Registering API routes")
app.include_router(character.router, prefix="/character", tags=["Characters"])
