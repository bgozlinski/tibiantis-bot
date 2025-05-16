import logging
from sqlalchemy.orm import Session
from app.scrapers.tibiantis_scraper import TibiantisScraper
from app.repositories.character_repository import CharacterRepository
from app.db.dependecies import get_db

logger = logging.getLogger(__name__)


def scrape_and_store_online_players():
    """
    Scrape online players from Tibiantis and store them in the database.
    This function is designed to be run as a scheduled task.
    """
    logger.info("Starting scheduled task: scrape_and_store_online_players")

    # Get database session
    db = next(get_db())

    try:
        # Create scraper and repository
        scraper = TibiantisScraper()
        repository = CharacterRepository(db)

        # Get online players
        online_players = scraper.get_online_players()
        logger.info(f"Found {len(online_players)} online players")

        # Process each player
        for player in online_players:
            try:
                # Check if player exists in database
                if not repository.exists_by_name(player["name"]):
                    # Add new player
                    logger.info(f"Adding new player to database: {player['name']}")
                    repository.add_by_name(player["name"])
                else:
                    # Update existing player
                    logger.info(f"Updating existing player: {player['name']}")
                    character = repository.get_by_name(player["name"])

                    # Update level and vocation if they've changed
                    update_data = {}
                    if character.level != player["level"]:
                        update_data["level"] = player["level"]

                    if update_data:
                        repository.update_character_by_id(character.id, update_data)

            except Exception as e:
                logger.error(f"Error processing player {player['name']}: {e}", exc_info=True)
                continue

        logger.info("Completed scheduled task: scrape_and_store_online_players")

    except Exception as e:
        logger.error(f"Error in scheduled task: {e}", exc_info=True)

    finally:
        db.close()