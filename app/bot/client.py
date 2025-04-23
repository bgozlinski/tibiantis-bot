import discord
from discord.ext import commands
from app.bot.config import DISCORD_CHANNEL_ID
from app.bot.commands import say_hello


class Client(commands.Bot):
    def __init__(self):
        print("Initializing bot...")
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            description="Discord bot for testing purposes"
        )
        self.allowed_channel_id = DISCORD_CHANNEL_ID

    async def setup_hook(self):
        print("Setting up bot...")
        try:
            self.tree.add_command(say_hello)

            print("Syncing commands...")
            synced = await self.tree.sync()  # Global sync
            print(f"Successfully synchronized {len(synced)} command(s)")
            print(f"Synchronized commands: {[cmd.name for cmd in synced]}")

        except Exception as e:
            print(f"Error during synchronization: {e}")

    async def on_ready(self):
        print(f"Bot logged in as {self.user} (ID: {self.user.id})")
        print(f"Bot is present in {len(self.guilds)} server(s):")
        for guild in self.guilds:
            print(f"- {guild.name} (ID: {guild.id})")
        print(f"Bot will only respond in channel ID: {self.allowed_channel_id}")