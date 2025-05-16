import asyncio
from datetime import datetime
import logging
import httpx
from discord.ext import tasks
from app.scrapers.tibiantis_scraper import TibiantisScraper
from app.bot.config import API_URL, TABLE_REFRESH_INTERVAL

logger = logging.getLogger(__name__)


class EnemyScraperTask:
    def __init__(self, bot):
        self.bot = bot
        self.scraper = TibiantisScraper()
        # Start the task loop
        self.scrape_enemies_loop.start()
        logger.info("Enemy scraper task initialized")

    def cog_unload(self):
        self.scrape_enemies_loop.cancel()
        logger.info("Enemy scraper task unloaded")

    @tasks.loop(minutes=TABLE_REFRESH_INTERVAL)
    async def scrape_enemies_loop(self):
        """Scrape data for all enemy characters periodically"""
        logger.info("Running enemy scraper task")
        try:
            # Get all enemy characters
            async with httpx.AsyncClient(verify=False) as client:
                characters_response = await client.get(f"{API_URL}/character/")
                characters = characters_response.json()
                enemies_response = await client.get(f"{API_URL}/enemy/")
                enemies = enemies_response.json()

                # Extract enemy character IDs
                enemy_character_ids = [enemy["character_id"] for enemy in enemies]

                # Get enemy characters
                enemy_characters = []
                for character in characters:
                    if character["id"] in enemy_character_ids:
                        enemy_characters.append(character)

                logger.info(f"Found {len(enemy_characters)} enemy characters to scrape")

                # Scrape data for each enemy character
                for character in enemy_characters:
                    try:
                        # Use the scraper to get character data
                        character_data = await asyncio.to_thread(
                            self.scraper.get_character_data,
                            character["name"]
                        )

                        if character_data:
                            # Update character data in the database
                            update_data = {
                                "level": character_data.get("level"),
                                "vocation": character_data.get("vocation"),
                                "last_login": character_data.get("last_login")
                            }

                            # Convert datetime to string if it exists
                            if "last_login" in update_data and update_data["last_login"] and isinstance(
                                    update_data["last_login"], datetime):
                                update_data["last_login"] = update_data["last_login"].isoformat()

                            # Remove None values
                            update_data = {k: v for k, v in update_data.items() if v is not None}

                            if update_data:
                                await client.patch(
                                    f"{API_URL}/character/{character['id']}",
                                    json=update_data
                                )
                                logger.info(f"Updated character data for {character['name']}")
                    except Exception as e:
                        logger.error(f"Error scraping data for {character['name']}: {e}", exc_info=True)

            logger.info("Enemy scraper task completed successfully")
        except Exception as e:
            logger.error(f"Error in enemy scraper task: {e}", exc_info=True)

    @scrape_enemies_loop.before_loop
    async def before_scrape_enemies(self):
        """Wait until the bot is ready before starting the task"""
        await self.bot.wait_until_ready()
        logger.info("Bot is ready, starting enemy scraper task")

        # Run the scraper immediately on bot start
        logger.info("Running initial enemy scraper on bot start")
        await self.scrape_enemies_loop()
        logger.info("Initial enemy scraper completed")