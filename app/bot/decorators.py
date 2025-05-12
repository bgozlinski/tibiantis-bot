import discord
import functools
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

def is_admin_or_moderator():
    """
    A decorator that checks if the user has administrator permissions or has a moderator role.

    This decorator can be used with Discord application commands to restrict
    access to users with administrator permissions or moderator role.

    Returns:
        Callable: The decorated function that will check for admin permissions or moderator role

    Example:
        @app_commands.command(name="admin_or_mod_command")
        @is_admin_or_moderator()
        async def admin_or_mod_command(interaction: discord.Interaction):
            await interaction.response.send_message("You are an admin or moderator!")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs) -> Any:
            # Check if the user has administrator permissions
            if interaction.user.guild_permissions.administrator:
                logger.info(f"Admin command used by {interaction.user.name} (ID: {interaction.user.id})")
                return await func(interaction, *args, **kwargs)

            # Check if the user has a moderator role
            has_moderator_role = any(role.name.lower() == "moderator" for role in interaction.user.roles)
            if has_moderator_role:
                logger.info(f"Moderator command used by {interaction.user.name} (ID: {interaction.user.id})")
                return await func(interaction, *args, **kwargs)

            # If neither admin nor moderator, deny access
            logger.warning(f"User {interaction.user.name} (ID: {interaction.user.id}) attempted to use admin/moderator command without permission")
            await interaction.response.send_message(
                "❌ You don't have permission to use this command. Administrator or Moderator privileges required.",
                ephemeral=True
            )
            return None

        return wrapper

    return decorator
