import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import character, enemy_character
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.tasks.player_scraper import scrape_and_store_online_players

logger = logging.getLogger(__name__)

# Create a scheduler instance
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("FastAPI application starting up")

    # Start the background scheduler
    logger.info("Starting background scheduler")
    scheduler.start()

    # Schedule the scraper to run every 5 minutes
    scheduler.add_job(
        scrape_and_store_online_players,
        trigger=IntervalTrigger(minutes=5),
        id="scrape_online_players",
        name="Scrape online players every 5 minutes",
        replace_existing=True
    )
    logger.info("Scheduled job: scrape_online_players (every 5 minutes)")

    # Run the scraper immediately once at startup
    scheduler.add_job(
        scrape_and_store_online_players,
        id="initial_scrape",
        name="Initial scrape of online players",
        replace_existing=True
    )

    yield

    # Shut down the scheduler when the application is shutting down
    logger.info("Shutting down background scheduler")
    scheduler.shutdown()
    logger.info("FastAPI application shutting down")


app = FastAPI(lifespan=lifespan)
logger.info("Registering API routes")


@app.get("/")
async def index():
    logger.debug("Health check endpoint called")
    return {"ping": "pong"}


app.include_router(character.router, prefix="/character", tags=["Characters"])
app.include_router(enemy_character.router, prefix="/enemy", tags=["Enemies"])