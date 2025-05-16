import discord
from discord import app_commands
from app.bot.decorators import is_admin_or_moderator


@app_commands.command(name="add_enemy", description="Adds a character to the enemy list")
async def add_enemy(interaction: discord.Interaction, character_name: str, reason: str = None):
    """
    Adds a character to the enemy list.
    Only users with administrator permissions or moderator role can use this command.

    Parameters:
        interaction (discord.Interaction): The interaction object
        character_name (str): The name of the character to add as an enemy
        reason (str, optional): The reason for marking the character as an enemy
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
            # Try to add the character first
            try:
                character = character_repository.add_by_name(character_name)
                await interaction.followup.send(
                    f"Character '{character_name}' was not in the database, but has been added automatically.",
                    ephemeral=True
                )
            except ValueError as e:
                await interaction.followup.send(
                    f"❌ Error: Character '{character_name}' does not exist on Tibiantis server.",
                    ephemeral=True
                )
                return

        # Get the character
        character = character_repository.get_by_name(character_name)

        # Check if character is already an enemy
        if enemy_repository.is_enemy(character.id):
            await interaction.followup.send(
                f"Character '{character_name}' is already marked as an enemy!",
                ephemeral=True
            )
            return

        # Add a character to an enemy list
        added_by = f"{interaction.user.name}#{interaction.user.discriminator}" if interaction.user.discriminator != '0' else interaction.user.name
        enemy = enemy_repository.add_enemy(
            character_id=character.id,
            reason=reason,
            added_by=added_by
        )

        await interaction.followup.send(
            f"✅ Successfully added **{character.name}** to the enemy list" +
            (f" with reason: *{reason}*" if reason else ""),
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