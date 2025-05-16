import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
ENEMY_KILLS_CHANNEL_ID = int(os.getenv("ENEMY_KILLS_CHANNEL_ID"))
TABLE_REFRESH_INTERVAL = int(os.getenv("TABLE_REFRESH_INTERVAL"))
API_URL = os.getenv("API_URL", "http://localhost:8000")