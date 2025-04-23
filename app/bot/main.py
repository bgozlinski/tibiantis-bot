import discord

from app.bot.client import Client
from app.bot.config import DISCORD_BOT_TOKEN


async def run_bot():
    client = Client()

    try:
        print("Starting bot...")
        await client.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("Failed to login. Please check your token.")
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")
        raise e