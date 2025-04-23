import asyncio
import uvicorn
import os
from dotenv import load_dotenv
from app.bot import run_bot

# Load environment variables from .env file
load_dotenv()

def run_uvicorn():
    # Get configuration from environment variables with defaults
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "True").lower() == "true"
    
    # Run the application with uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

def bot_process_target():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()


if __name__ == "__main__":
    import multiprocessing
    
    # Uruchom bota w osobnym procesie
    bot_process = multiprocessing.Process(target=bot_process_target)
    bot_process.start()
    
    # Uruchom API w głównym procesie
    run_uvicorn()