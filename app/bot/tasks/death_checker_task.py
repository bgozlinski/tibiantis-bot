import asyncio
import logging
from discord.ext import tasks
from app.tasks.death_checker import check_character_deaths_by_enemies
from app.bot.config import TABLE_REFRESH_INTERVAL

logger = logging.getLogger(__name__)

class DeathCheckerTask:
    def __init__(self, bot):
        self.bot = bot
        self.check_deaths_loop.start()
        logger.info("Death checker task initialized")

    def cog_unload(self):
        self.check_deaths_loop.cancel()
        logger.info("Death checker task unloaded")

    @tasks.loop(minutes=TABLE_REFRESH_INTERVAL)
    async def check_deaths_loop(self):
        """Run the death checker periodically"""
        logger.info("Running death checker task")
        try:
            await check_character_deaths_by_enemies()
            logger.info("Death checker task completed successfully")
        except Exception as e:
            logger.error(f"Error in death checker task: {e}", exc_info=True)

    @check_deaths_loop.before_loop
    async def before_check_deaths(self):
        """Wait until the bot is ready before starting the task"""
        await self.bot.wait_until_ready()
        logger.info("Bot is ready, starting death checker task")