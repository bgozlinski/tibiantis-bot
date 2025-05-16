import logging
import asyncio
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from app.scrapers.tibiantis_scraper import TibiantisScraper
from app.repositories.character_repository import CharacterRepository
from app.repositories.enemy_character_repository import EnemyCharacterRepository
from app.bot.client import get_bot_instance
from app.tasks.base_task import BaseTask
import datetime
from dateutil import tz

logger = logging.getLogger(__name__)


class DeathCheckerTask(BaseTask):
    """
    Task for checking if characters were killed by enemy characters.
    """
    
    def __init__(self):
        """Initialize the task."""
        self.scraper = TibiantisScraper()
    
    async def check_character_deaths_by_enemies(self):
        """
        Check if any characters in the database were killed by enemy characters.
    
        This method:
        1. Retrieves all characters from the database
        2. Retrieves all enemy characters from the database
        3. For each character, checks their death history
        4. Determines if any deaths were caused by an enemy character
        5. Reports the results via Discord and logs
    
        Returns:
            List[Dict]: List of death entries where a character was killed by an enemy
        """
        logger.info("Starting task: check_character_deaths_by_enemies")
        
        try:
            with self.get_db_session() as db:
                # Create repositories
                character_repo = CharacterRepository(db)
                enemy_repo = EnemyCharacterRepository(db)
        
                # Get all characters and enemy characters
                enemies = enemy_repo.get_all()
        
                # Filter characters with level >= 30
                high_level_characters = character_repo.get_high_level_characters(min_level=30)
        
                # Create a set of enemy character names for faster lookup
                enemy_names = {enemy.character.name.lower() for enemy in enemies if enemy.character and enemy.character.name}
        
                logger.info(
                    f"Checking {len(high_level_characters)} high-level characters against {len(enemy_names)} enemy names")
        
                # Create tasks for all characters to process them in parallel
                tasks = [
                    self._process_character_deaths(character, enemy_names)
                    for character in high_level_characters
                ]
        
                # Execute all tasks concurrently and gather results
                results = await asyncio.gather(*tasks, return_exceptions=True)
        
                # Process results and filter out exceptions
                killed_by_enemies = []
                for character, result in zip(high_level_characters, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing {character.name}: {result}")
                    elif result:  # If we got valid death entries
                        killed_by_enemies.extend(result)
        
                # Report the results
                if killed_by_enemies:
                    logger.info(f"Found {len(killed_by_enemies)} instances of characters killed by enemies")
                    await self._send_enemy_kills_table(killed_by_enemies)
                else:
                    logger.info("No characters were killed by enemies")
        
                return killed_by_enemies
        
        except Exception as e:
            logger.error(f"Error in task: {e}", exc_info=True)
            return []
    
    async def _process_character_deaths(self, character, enemy_names):
        """
        Process deaths for a single character.
        
        Parameters:
            character: Character entity
            enemy_names: Set of enemy character names
            
        Returns:
            List[Dict]: List of death entries where the character was killed by an enemy
        """
        if not character.name:
            return []
    
        logger.info(f"Checking death history for character: {character.name}")
    
        # Get death information
        deaths = await self.scraper.get_character_deaths_async(character.name)
        killed_entries = []
    
        # Check if any deaths were caused by an enemy
        for death in deaths:
            killer = death.get("killer", "")
            time = death.get("time")
    
            # Skip deaths older than 12 hours
            if not time or time < datetime.datetime.now(tz=tz.tzlocal()) - datetime.timedelta(hours=12):
                continue
    
            # Extract the killer name from the death message
            if "by" in killer:
                killer_string = killer.split("by")[-1].strip().lower().replace(".", "")
    
                # Handle multiple killers (separated by "and")
                killer_names = [name.strip() for name in killer_string.split(" and ")]
    
                # Check if any of the killers are in our enemy list
                for killer_name in killer_names:
                    if killer_name in enemy_names:
                        logger.info(f"Character {character.name} was killed by enemy: {killer}")
    
                        killed_entries.append({
                            "character_name": character.name,
                            "time": death.get("time"),
                            "killer": killer
                        })
                        # Break after finding the first enemy killer to avoid duplicate entries
                        break
    
        return killed_entries
    
    async def _send_enemy_kills_table(self, killed_by_enemies: List[Dict]):
        """
        Send a formatted table of enemy kills to the specified Discord channel.
        
        Parameters:
            killed_by_enemies: List of death entries where a character was killed by an enemy
        """
        try:
            from app.bot.client import get_bot_instance
            from app.bot.config import ENEMY_KILLS_CHANNEL_ID
    
            bot = get_bot_instance()
            if not bot:
                logger.error("Bot instance not available")
                return
    
            channel = bot.get_channel(ENEMY_KILLS_CHANNEL_ID)
            if not channel:
                logger.error(f"Could not find channel with ID {ENEMY_KILLS_CHANNEL_ID}")
                return
    
            # Delete previous enemy kills table messages
            try:
                # Look through the last 50 messages in the channel
                async for message in channel.history(limit=50):
                    # Check if the message was sent by the bot and contains the enemy kills table header
                    if message.author.id == bot.user.id and "📊 **ENEMY KILLS TABLE** 📊" in message.content:
                        await message.delete()
                        logger.info("Deleted previous enemy kills table message")
            except Exception as e:
                logger.error(f"Error deleting previous messages: {e}")
                # Continue with sending the new message even if deletion fails
    
            # Format the message as a table
            message = "📊 **ENEMY KILLS TABLE** 📊\n\n"
    
            if not killed_by_enemies:
                message += "No enemy kills recorded recently."
            else:
                # Sort the deaths by time (newest first)
                killed_by_enemies = sorted(killed_by_enemies, key=lambda x: x["time"] if x["time"] else datetime.datetime.min, reverse=True)
    
                # Add table header
                message += "```\n"
                message += f"{'Killer':<30} {'Victim':<20} {'Time':<20}\n"
                message += "-" * 70 + "\n"
    
                # Add table rows
                for death in killed_by_enemies:
                    # Extract the killer name from the death message
                    killer = death["killer"]
                    if "by" in killer:
                        killer_string = killer.split("by")[-1].strip().replace(".", "")
    
                        # Handle multiple killers (separated by "and")
                        if " and " in killer_string:
                            # Format multiple killers nicely for display
                            killer_name = killer_string
                        else:
                            killer_name = killer_string
                    else:
                        killer_name = killer
    
                    # Format the time
                    time_str = death["time"].strftime("%Y-%m-%d %H:%M") if death["time"] else "Unknown"
    
                    # Add the row to the table
                    # Capitalize each word in the killer name for better readability
                    formatted_killer_name = ' '.join(word.capitalize() for word in killer_name.split())
                    message += f"{formatted_killer_name[:29]:<30} {death['character_name'][:19]:<20} {time_str:<20}\n"
    
                message += "```"
    
            # Send the message
            await channel.send(message)
            logger.info(f"Sent enemy kills table with {len(killed_by_enemies)} entries")
    
        except Exception as e:
            logger.error(f"Error sending enemy kills table: {e}", exc_info=True)


# Create a singleton instance for use in scheduled tasks
death_checker_task = DeathCheckerTask()

# Function to maintain backward compatibility with existing code
async def check_character_deaths_by_enemies():
    """
    Check if any characters in the database were killed by enemy characters.
    
    This function is a wrapper around DeathCheckerTask.check_character_deaths_by_enemies
    for backward compatibility.
    
    Returns:
        List[Dict]: List of death entries where a character was killed by an enemy
    """
    return await death_checker_task.check_character_deaths_by_enemies()