import discord
import logging

from app.bot.client import Client
from app.bot.config import DISCORD_BOT_TOKEN

logger = logging.getLogger(__name__)


async def run_bot():
    client = Client()

    try:
        logger.info("Starting Discord bot...")
        await client.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("Failed to login to Discord. Please check your token.")
    except Exception as e:
        logger.exception(f"An error occurred while running the Discord bot: {e}")
        raise e
