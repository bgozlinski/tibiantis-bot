import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.character import Character
from app.db.schemas.character import CharacterAdd
from app.scrapers.tibiantis_scraper import TibiantisScraper

logger = logging.getLogger(__name__)


class CharacterRepository:
    """
    Repository class for managing Character entities in the database.

    This class provides an abstraction layer between the database and the application,
    handling all database operations related to Character entities.

    Attributes:
        db (Session): SQLAlchemy database session instance

    Example:
        def create_new_character(db_session: Session):
            repo = CharacterRepository(db_session)
            new_character = CharacterCreate(name="Karius", last_seen_location="Thais")
            character = repo.create(new_character)
            return character
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Parameters:
            db (Session): SQLAlchemy database session
        """

        self.db = db

    def get_all(self) -> List[Character]:
        """
        Retrieve all characters from the database.

        Returns:
            List[Character]: List of all Character entities

        Example:
            repo = CharacterRepository(db_session)
            all_characters = repo.get_all()
        """

        return self.db.query(Character).all()  # type: ignore

    def get_by_id(self, character_id: int) -> Optional[Character]:
        """
        Retrieve a character by their ID.

        Parameters:
            character_id (int): The ID of the character to retrieve

        Returns:
            Optional[Character]: Found character entity or None if not found

        Example:
            repo = CharacterRepository(db_session)
            character = repo.get_by_id(1)
        """

        return self.db.query(Character).filter(Character.id == character_id).first()

    def exists_by_name(self, name: str) -> bool:
        """
        Check if a character with the given name exists.

        Parameters:
            name (str): Character name to check

        Returns:
            bool: True if a character exists, False otherwise

        Example:
            repo = CharacterRepository(db_session)
            exists = repo.exists_by_name("Karius")
        """

        return self.db.query(Character).filter(Character.name == name).first() is not None

    def add_by_name(self, character_name: str) -> Character:
        """
        Start tracking an existing Tibiantis Online character.

        Parameters:
            character_name (str): Name of the character to track

        Returns:
            Character: Data of the character that is now being tracked

        Raises:
            ValueError: If the character does not exist on Tibiantis server
            Exception: If there's an error in adding the character to the database

        Example:
            repo = CharacterRepository(db_session)
            character = repo.add_by_name("Karius")
        """
        scraper = TibiantisScraper()
        logger.info(f"Fetching character data for: {character_name}")
        scraped_data = scraper.get_character_data(character_name)
        logger.debug(f"Scraped data for {character_name}: {scraped_data}")

        if not scraped_data:
            logger.warning(f"No scraped data found for character: {character_name}. Cannot add non-existent character.")
            raise ValueError(f"Character '{character_name}' does not exist on Tibiantis server")

        character_data = CharacterAdd(name=character_name)
        full_character_data = {**character_data.model_dump(), **scraped_data}
        character = Character(**full_character_data)

        try:
            self.db.add(character)
            self.db.commit()
            self.db.refresh(character)
            logger.info(f"Successfully added character to database: {character.name} (ID: {character.id})")
        except Exception as e:
            logger.error(f"Error adding character to database: {e}", exc_info=True)
            self.db.rollback()
            raise

        return character

    def delete_character_by_id(self, character_id: int):
        """
        Delete a character by ID.

        Parameters:
            character_id (int): The ID of the character to delete

        Returns:
            dict: A dictionary with a detail message confirming deletion

        Raises:
            Exception: If there's an error in deleting the character from the database

        Example:
            repo = CharacterRepository(db_session)
            result = repo.delete_character_by_id(1)
        """
        character = self.get_by_id(character_id)
        logger.info(f"Deleting character: {character.name} (ID: {character.id})")

        try:
            self.db.delete(character)
            self.db.commit()
            logger.info(f"Successfully deleted character: {character.name} (ID: {character.id})")
        except Exception as e:
            logger.error(f"Error deleting character from database: {e}", exc_info=True)
            raise

        return {"detail": f"Deleted character: {character.name} (ID: {character.id})"}


    def update_character_name_by_id(self, character_id: int, new_name: str) ->Optional[Character]:
        character = self.get_by_id(character_id)

        if not character:
            return None

        logger.info(f"Updating character name: {character.name} (ID: {character.id}) to {new_name}")

        character.name = new_name

        try:
            self.db.commit()
            self.db.refresh(character)
            logger.info(f"Successfully updated character: {character.name} (ID: {character.id})")
        except Exception as e:
            logger.error(f"Error updating character name in database: {e}", exc_info=True)
            self.db.rollback()
            raise

        return character



