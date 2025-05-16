import logging
from sqlalchemy.orm import Session
from app.scrapers.tibiantis_scraper import TibiantisScraper
from app.repositories.character_repository import CharacterRepository
from app.tasks.base_task import BaseTask

logger = logging.getLogger(__name__)


class PlayerScraperTask(BaseTask):
    """
    Task for scraping online players from Tibiantis and storing them in the database.
    """

    def __init__(self):
        """Initialize the task."""
        self.scraper = TibiantisScraper()

    def _process_player(self, db: Session, player: dict):
        """
        Process a single player.

        Parameters:
            db (Session): Database session
            player (dict): Player data
        """
        repository = CharacterRepository(db)

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

    def scrape_and_store_online_players(self):
        """
        Scrape online players from Tibiantis and store them in the database.
        This method is designed to be run as a scheduled task.
        """
        logger.info("Starting scheduled task: scrape_and_store_online_players")

        try:
            # Get online players
            online_players = self.scraper.get_online_players()
            logger.info(f"Found {len(online_players)} online players")

            # Process each player with a database session
            with self.get_db_session() as db:
                for player in online_players:
                    self._process_player(db, player)

            logger.info("Completed scheduled task: scrape_and_store_online_players")

        except Exception as e:
            logger.error(f"Error in scheduled task: {e}", exc_info=True)


# Create a singleton instance for use in scheduled tasks
player_scraper_task = PlayerScraperTask()

# Function to maintain backward compatibility with existing code
def scrape_and_store_online_players():
    """
    Scrape online players from Tibiantis and store them in the database.
    This function is designed to be run as a scheduled task.
    """
    player_scraper_task.scrape_and_store_online_players()
