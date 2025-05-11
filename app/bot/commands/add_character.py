import discord
from discord import app_commands

@app_commands.command(name="add_character", description="Adds a new character to tracking database")
async def add_character(interaction: discord.Interaction, character_name: str):
    """
    Adds a new character to the tracking database.

    Parameters:
        interaction (discord.Interaction): The interaction object
        character_name (str): The name of the character to add
    """

    await interaction.response.defer(thinking=True)

    from app.db.session import SessionLocal
    from app.repositories.character_repository import CharacterRepository

    db = SessionLocal()
    try:
        repository = CharacterRepository(db)

        if repository.exists_by_name(character_name):
            await interaction.followup.send(
                f"Character '{character_name}' is already being tracked!",
                ephemeral=True
            )
            return

        character = repository.add_by_name(character_name)

        await interaction.followup.send(
            f"✅ Successfully added character: **{character.name}**",
            ephemeral=True
        )

    except ValueError as e:
        await interaction.followup.send(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"❌ An unexpected error occurred: {str(e)}",
            ephemeral=True
        )
    finally:
        db.close()
