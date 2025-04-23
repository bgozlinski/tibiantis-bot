import discord
from discord import app_commands

from app.bot.config import DISCORD_CHANNEL_ID


@app_commands.command(name="hello", description="Sends a greeting message")
async def say_hello(interaction: discord.Interaction):
    """Sends a hello message"""
    if interaction.channel_id != DISCORD_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the designated channel!",
            ephemeral=True
        )
        return

    await interaction.response.send_message(f"Hello {interaction.user.mention}!")

