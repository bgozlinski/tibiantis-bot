import asyncio
import datetime
import httpx
import logging
from app.bot.config import API_URL
from app.scrapers.tibiantis_scraper import TibiantisScraper
from dateutil import tz

logger = logging.getLogger(__name__)


async def refresh_character_death_and_update_table():
    async with asyncio.Lock():
        try:
            async with httpx.AsyncClient() as client:
                characters_response = await client.get(f"{API_URL}/character/")
                characters = characters_response.json()
                enemies_response = await client.get(f"{API_URL}/enemy/")
                enemies = enemies_response.json()

                # Extract enemy character names
                enemy_character_ids = [enemy["character_id"] for enemy in enemies]

                # Get character names by their IDs
                enemy_characters = []
                for character in characters:
                    if character["id"] in enemy_character_ids:
                        enemy_characters.append(character)

                enemy_character_names = [character["name"] for character in enemy_characters]
                print(f"Enemy characters: {enemy_character_names}")

                scraper_instance = TibiantisScraper()

                async def get_characters_death_async(character_name):
                    return await asyncio.to_thread(
                        scraper_instance.get_character_deaths,
                        character_name
                    )

                # Filter characters with level >= 30 before creating tasks
                high_level_characters = [character for character in characters if character["level"] >= 30]

                tasks = [
                    get_characters_death_async(character["name"])
                    for character in high_level_characters
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Now zip only the high level characters with their results
                for character, result in zip(high_level_characters, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing {character['name']}: {result}")
                    else:
                        enemy_deaths = [
                            death for death in result
                            if death["time"] and death["time"] >= datetime.datetime.now(
                                tz=tz.tzlocal()) - datetime.timedelta(hours=12)
                               and any(enemy_name in death["killer"] for enemy_name in enemy_character_names)
                        ]

                        if enemy_deaths:
                            print(f"Enemy deaths for {character['name']}: {enemy_deaths}")
                            # Process the enemy death data as needed

                    # Update the character table or perform other operations
                await send_enemy_table()

        except Exception as e:
            logger.error(f"Error refreshing character deaths: {e}", exc_info=True)


async def send_enemy_table():
    """Send a formatted table of enemy characters to the Discord channel"""
    try:
        from app.bot.client import get_bot_instance
        bot = get_bot_instance()

        if not bot:
            logger.error("Bot instance not available")
            return

        channel = bot.get_channel(int(bot.allowed_channel_id))
        if not channel:
            logger.error(f"Could not find channel with ID {bot.allowed_channel_id}")
            return

        # Delete previous enemy table messages
        try:
            # Look through the last 50 messages in the channel
            async for message in channel.history(limit=50):
                # Check if the message was sent by the bot and contains the enemy table header
                if message.author.id == bot.user.id and "📊 **ENEMY CHARACTERS LIST** 📊" in message.content:
                    await message.delete()
                    logger.info("Deleted previous enemy table message")
        except Exception as e:
            logger.error(f"Error deleting previous messages: {e}")
            # Continue with sending the new message even if deletion fails

        # Get enemy data
        async with httpx.AsyncClient() as client:
            characters_response = await client.get(f"{API_URL}/character/")
            characters = characters_response.json()
            enemies_response = await client.get(f"{API_URL}/enemy/")
            enemies = enemies_response.json()

        # Extract enemy character information
        enemy_character_ids = [enemy["character_id"] for enemy in enemies]
        enemy_reasons = {enemy["character_id"]: enemy.get("reason", "No reason provided") for enemy in enemies}
        enemy_added_by = {enemy["character_id"]: enemy.get("added_by", "Unknown") for enemy in enemies}

        # Get character details by their IDs
        enemy_characters = []
        for character in characters:
            if character["id"] in enemy_character_ids:
                character_info = {
                    "id": character["id"],
                    "name": character["name"],
                    "level": character.get("level", "Unknown"),
                    "vocation": character.get("vocation", "Unknown"),
                    "reason": enemy_reasons.get(character["id"], "-"),
                    "added_by": enemy_added_by.get(character["id"], "Unknown")
                }
                enemy_characters.append(character_info)

        # Sort enemies by level (descending)
        enemy_characters.sort(key=lambda x: x["level"] if isinstance(x["level"], int) else 0, reverse=True)

        # Format the message
        message = "📊 **ENEMY CHARACTERS LIST** 📊\n\n"

        if not enemy_characters:
            message += "No enemy characters currently tracked."
        else:
            # Add table header
            message += "```\n"
            message += f"{'Name':<20} {'Level':<6} {'Vocation':<12} {'Reason':<30}\n"
            message += "-" * 70 + "\n"

            # Add table rows
            for enemy in enemy_characters:
                name = enemy["name"][:19]
                level = str(enemy["level"])[:5]
                vocation = str(enemy["vocation"])[:11]
                reason = str(enemy["reason"] or "No reason provided")[:29]

                message += f"{name:<20} {level:<6} {vocation:<12} {reason:<30}\n"

            message += "```"

        # Send the message
        await channel.send(message)
        logger.info(f"Sent enemy table with {len(enemy_characters)} enemies")

    except Exception as e:
        logger.error(f"Error sending enemy table: {e}", exc_info=True)


def update_character_table():
    """Legacy function - now calls the async version"""
    asyncio.create_task(send_enemy_table())
