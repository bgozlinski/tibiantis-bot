import discord
import logging
from discord.ext import commands
from app.bot.config import DISCORD_CHANNEL_ID
from app.bot.commands import say_hello, add_character

logger = logging.getLogger(__name__)


class Client(commands.Bot):
    def __init__(self):
        logger.info("Initializing Discord bot...")
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            description="Discord bot for testing purposes"
        )
        self.allowed_channel_id = DISCORD_CHANNEL_ID

    async def setup_hook(self):
        logger.info("Setting up Discord bot...")
        try:
            self.tree.add_command(say_hello)
            self.tree.add_command(add_character)

            logger.info("Syncing Discord commands...")
            synced = await self.tree.sync()  # Global sync
            logger.info(f"Successfully synchronized {len(synced)} command(s)")
            logger.debug(f"Synchronized commands: {[cmd.name for cmd in synced]}")

        except Exception as e:
            logger.error(f"Error during Discord command synchronization: {e}", exc_info=True)

    async def on_ready(self):
        logger.info(f"Discord bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Discord bot is present in {len(self.guilds)} server(s)")

        for guild in self.guilds:
            logger.debug(f"- {guild.name} (ID: {guild.id})")

        logger.info(f"Discord bot will only respond in channel ID: {self.allowed_channel_id}")
