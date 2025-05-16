import discord
import logging
from discord.ext import commands

from app.bot.commands.add_character_enemy import add_enemy
from app.bot.commands.remove_character_enemy import remove_enemy
from app.bot.config import DISCORD_CHANNEL_ID
from app.bot.commands.add_character import add_character
from app.bot.commands.delete_character import delete_character
from app.bot.commands.update_character import change_name

logger = logging.getLogger(__name__)

# Global bot instance
_bot_instance = None


def get_bot_instance():
    """Returns the global bot instance"""
    return _bot_instance


class Client(commands.Bot):
    def __init__(self):
        logger.info("Initializing Discord bot...")
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            description="Discord bot for testing purposes"
        )
        self.allowed_channel_id = DISCORD_CHANNEL_ID

        # Set the global bot instance
        global _bot_instance
        _bot_instance = self

    async def setup_hook(self):
        logger.info("Setting up Discord bot...")
        try:
            self.tree.add_command(add_character)
            self.tree.add_command(delete_character)
            self.tree.add_command(change_name)
            self.tree.add_command(add_enemy)
            self.tree.add_command(remove_enemy)

            # Initialize death checker task
            from app.bot.tasks.death_checker_task import DeathCheckerTask
            self.death_checker = DeathCheckerTask(self)
            logger.info("Death checker task initialized")

            logger.info("Syncing Discord commands...")
            synced = await self.tree.sync()  # Global sync
            logger.info(f"Successfully synchronized {len(synced)} command(s)")
            logger.debug(f"Synchronized commands: {[cmd.name for cmd in synced]}")

        except Exception as e:
            logger.error(f"Error during Discord command synchronization: {e}", exc_info=True)

    async def on_ready(self):
        logger.info(f"Discord bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Discord bot is present in {len(self.guilds)} server(s)")

        # Send initial enemy table
        from app.bot.enemy_table_manager import send_enemy_table
        await send_enemy_table()