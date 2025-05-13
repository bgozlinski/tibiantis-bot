import datetime
import logging
from discord.ext import tasks
from app.bot.config import DISCORD_CHANNEL_ID

logger = logging.getLogger(__name__)


class BotTasks:
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = DISCORD_CHANNEL_ID

    def start_tasks(self):
        """Start all periodic tasks"""
        self.periodic_message_test.start()

    @tasks.loop(seconds=30)
    async def periodic_message_test(self):
        """Send a formatted message to the specified channel every 30 seconds."""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                # Clean the channel before sending a new message
                await self.clean_channel(channel)

                # Create a message with Markdown formatting
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                markdown_message = (
                    "# Automated Update\n"
                    "## Status Report\n\n"
                    f"**Current Time**: {current_time}\n\n"
                    "### System Information\n"
                    "- ✅ Bot is running\n"
                    "- 📊 Channel is active\n"
                    "- 🕒 Next update in 30 seconds\n\n"
                    "_This is an automated message_"
                )

                # Send the formatted message
                await channel.send(markdown_message)
                logger.info(f"Sent periodic message to channel {self.channel_id}")
            else:
                logger.error(f"Could not find channel with ID {self.channel_id}")
        except Exception as e:
            logger.error(f"Error sending periodic message: {e}", exc_info=True)

    async def clean_channel(self, channel):
        """Clean the channel by deleting previous messages."""
        try:
            # Delete the last 10 messages (adjust as needed)
            deleted = await channel.purge(limit=10)
            logger.info(f"Cleaned {len(deleted)} messages from channel {self.channel_id}")
        except Exception as e:
            logger.error(f"Error cleaning channel: {e}", exc_info=True)

    @periodic_message_test.before_loop
    async def before_periodic_message(self):
        await self.bot.wait_until_ready()