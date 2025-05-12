import discord
from discord import app_commands
from app.bot.decorators import is_admin_or_moderator

@app_commands.command(name="delete_character", description="Deletes a character from tracking database")
@is_admin_or_moderator()
async def delete_character(interaction: discord.Interaction, character_name: str):
    """
    Deletes a character from the tracking database.
    Only users with administrator permissions or moderator role can use this command.

    Parameters:
        interaction (discord.Interaction): The interaction object
        character_name (str): The name of the character to delete
    """

    await interaction.response.defer(thinking=True, ephemeral=True)

    from app.db.session import SessionLocal
    from app.repositories.character_repository import CharacterRepository

    db = SessionLocal()
    try:
        repository = CharacterRepository(db)

        if not repository.exists_by_name(character_name):
            await interaction.followup.send(
                f"Character '{character_name}' is not being tracked!",
                ephemeral=True
            )
            return

        repository.delete_character_by_name(character_name)

        await interaction.followup.send(
            f"✅ {character_name} successfully deleted from tracking database!",
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
