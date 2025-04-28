import asyncio
import uvicorn
import os
import logging
from dotenv import load_dotenv
from app.bot import run_bot
from app.utils.logging import setup_logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def run_uvicorn():
    # Get configuration from environment variables with defaults
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "True").lower() == "true"

    logger.info(f"Starting API server on {host}:{port} (reload={reload})")

    # Run the application with uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

def bot_process_target():
    logger.info("Starting Discord bot process")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Bot process interrupted by user")
        loop.stop()
    except Exception as e:
        logger.error(f"Error in bot process: {e}", exc_info=True)
        raise
    finally:
        logger.info("Closing bot process event loop")
        loop.close()


if __name__ == "__main__":
    import multiprocessing

    logger.info("Starting Tibiantis-Bot application")

    # Start the bot in a separate process
    logger.info("Initializing Discord bot process")
    bot_process = multiprocessing.Process(target=bot_process_target)
    bot_process.start()
    logger.info(f"Discord bot process started with PID: {bot_process.pid}")

    # Run the API in the main process
    logger.info("Starting API server in main process")
    run_uvicorn()
