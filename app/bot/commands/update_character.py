import discord
from discord import app_commands

@app_commands.command(name="change_name", description="Changes a character name from tracking database")
async def change_name(interaction: discord.Interaction, old_name: str, new_name: str):

    await interaction.response.defer(thinking=True, ephemeral=True)

    from app.db.session import SessionLocal
    from app.repositories.character_repository import CharacterRepository

    db = SessionLocal()
    try:
        repository = CharacterRepository(db)

        if not repository.exists_by_name(old_name):
            await interaction.followup.send(
                f"⚠️ Character '{old_name}' is not being tracked!",
                ephemeral=True
            )
            return

        repository.change_character_name(old_name, new_name)

        await interaction.followup.send(
            f"✅ Successfully changed {old_name} to {new_name} in database!",
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
