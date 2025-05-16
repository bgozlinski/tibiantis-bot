import discord
from discord import app_commands
from app.bot.decorators import is_admin_or_moderator


@app_commands.command(name="remove_enemy", description="Removes a character from the enemy list")
@is_admin_or_moderator()
async def remove_enemy(interaction: discord.Interaction, character_name: str):
    """
    Removes a character from the enemy list.
    Only users with administrator permissions or moderator role can use this command.

    Parameters:
        interaction (discord.Interaction): The interaction object
        character_name (str): The name of the character to remove from the enemy list
    """

    await interaction.response.defer(thinking=True, ephemeral=True)

    from app.db.session import SessionLocal
    from app.repositories.character_repository import CharacterRepository
    from app.repositories.enemy_character_repository import EnemyCharacterRepository

    db = SessionLocal()
    try:
        character_repository = CharacterRepository(db)
        enemy_repository = EnemyCharacterRepository(db)

        # Check if character exists in the database
        if not character_repository.exists_by_name(character_name):
            await interaction.followup.send(
                f"Character '{character_name}' is not being tracked!",
                ephemeral=True
            )
            return

        # Get the character
        character = character_repository.get_by_name(character_name)

        # Check if a character is an enemy
        if not enemy_repository.is_enemy(character.id):
            await interaction.followup.send(
                f"Character '{character_name}' is not marked as an enemy!",
                ephemeral=True
            )
            return

        # Remove character from an enemy list
        enemy_repository.remove_enemy(character.id)

        await interaction.followup.send(
            f"✅ Successfully removed **{character.name}** from the enemy list",
            ephemeral=True
        )

        # Refresh the enemy table
        if interaction.client.enemy_table_manager:
            await interaction.client.enemy_table_manager.update_enemy_table()

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