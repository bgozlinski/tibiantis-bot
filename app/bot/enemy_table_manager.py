import discord
import asyncio
import logging
from typing import Optional
from discord.ext import tasks

from app.db.session import SessionLocal
from app.repositories.enemy_character_repository import EnemyCharacterRepository
from app.bot.config import DISCORD_CHANNEL_ID, TABLE_REFRESH_INTERVAL

logger = logging.getLogger(__name__)


class EnemyTableManager:
    """
    Manages the enemy table display in a Discord channel.
    Handles periodic updates and refreshes when enemies are added or removed.
    """

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = DISCORD_CHANNEL_ID
        self.last_message_id = None
        self.refresh_task = None

    async def start(self):
        """Start the periodic refresh task and post an initial table"""
        logger.info("Starting enemy table manager")
        self.refresh_task = self.refresh_enemy_table.start()

    def stop(self):
        """Stop the periodic refresh task"""
        if self.refresh_task and not self.refresh_task.is_being_cancelled():
            self.refresh_task.cancel()
            logger.info("Enemy table refresh task stopped")

    @tasks.loop(minutes=TABLE_REFRESH_INTERVAL)
    async def refresh_enemy_table(self):
        """Refresh the enemy table every TABLE_REFRESH_INTERVAL timer"""
        logger.info("Refreshing enemy table (scheduled)")
        await self.update_enemy_table()

    async def update_enemy_table(self):
        """Update the enemy table in the Discord channel"""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            logger.error(f"Could not find channel with ID {self.channel_id}")
            return

        # Generate the enemy table content
        table_content = await self.generate_enemy_table()

        try:
            # Delete all messages in the channel
            try:
                # Check if we can purge messages (requires manage_messages permission)
                await channel.purge(limit=100)
                logger.info(f"Purged messages from channel {channel.name}")
            except (discord.Forbidden, discord.HTTPException) as e:
                logger.warning(f"Could not purge messages from channel: {e}")

                # Fallback: try to delete messages one by one
                try:
                    async for message in channel.history(limit=100):
                        await message.delete()
                    logger.info(f"Deleted messages one by one from channel {channel.name}")
                except (discord.Forbidden, discord.HTTPException) as e:
                    logger.warning(f"Could not delete messages one by one: {e}")

            # Send a new message
            if table_content:
                message = await channel.send(table_content)
                self.last_message_id = message.id
                logger.info("Enemy table updated successfully")
            else:
                logger.info("No enemies to display in table")
        except Exception as e:
            logger.error(f"Error updating enemy table: {e}", exc_info=True)

    async def generate_enemy_table(self) -> Optional[str]:
        """Generate the enemy table content"""
        db = SessionLocal()
        try:
            enemy_repository = EnemyCharacterRepository(db)

            # Get all enemy characters
            enemies = enemy_repository.get_all()

            if not enemies:
                return "**Enemy Characters:** No characters are currently marked as enemies."

            # Create a fixed-width table format
            header = f"{'NAME':<15} {'LEVEL':<6} {'VOCATION':<20} {'REASON':<20} {'ADDED BY':<15}\n"
            separator = "-" * 80 + "\n"

            # Create table rows
            table_rows = []
            for enemy in enemies:
                character = enemy.character
                name = (character.name or "?")[:14]  # Limit length to prevent formatting issues
                level = str(character.level or "?")
                vocation = (character.vocation or "?")[:19]
                reason = (enemy.reason or "-")[:19]
                added_by = (enemy.added_by or "-")[:14]

                # Format the row with fixed width columns
                row = f"{name:<15} {level:<6} {vocation:<20} {reason:<20} {added_by:<15}"
                table_rows.append(row)

            # Combine all parts of the table
            table = header + separator + "\n".join(table_rows)

            # Return the formatted message
            return f"**Enemy Characters:**\n```\n{table}\n```"

        except Exception as e:
            logger.error(f"Error generating enemy table: {e}", exc_info=True)
            return None
        finally:
            db.close()