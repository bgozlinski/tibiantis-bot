import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from discord import app_commands

load_dotenv()

# Get environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))


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
            print("Registering commands...")
            # Now we register commands globally instead of for a specific guild
            self.tree.add_command(
                discord.app_commands.Command(
                    name="hello",
                    description="Sends a greeting message",
                    callback=self.say_hello
                )
            )

            print("Syncing commands...")
            synced = await self.tree.sync()  # Global sync
            print(f"Successfully synchronized {len(synced)} command(s)")
            print(f"Synchronized commands: {[cmd.name for cmd in synced]}")

        except Exception as e:
            print(f"Error during synchronization: {e}")

    async def say_hello(self, interaction: discord.Interaction):
        if interaction.channel_id != self.allowed_channel_id:
            await interaction.response.send_message(
                "This command can only be used in the designated channel!",
                ephemeral=True
            )
            return

        await interaction.response.send_message("Hello!")

    async def on_ready(self):
        print(f"Bot logged in as {self.user} (ID: {self.user.id})")
        print(f"Bot is present in {len(self.guilds)} server(s):")
        for guild in self.guilds:
            print(f"- {guild.name} (ID: {guild.id})")
        print(f"Bot will only respond in channel ID: {self.allowed_channel_id}")


def main():
    client = Client()

    try:
        print("Starting bot...")
        client.run(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("Failed to login. Please check your token.")
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")


if __name__ == "__main__":
    main()
