import logging
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.db.models.enemy_character import EnemyCharacter
from app.db.models.character import Character
from app.repositories.character_repository import CharacterRepository
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class EnemyCharacterRepository(BaseRepository[EnemyCharacter]):
    """
    Repository class for managing EnemyCharacter entities in the database.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Parameters:
            db (Session): SQLAlchemy database session
        """
        super().__init__(db, EnemyCharacter)
        self.character_repository = CharacterRepository(db)

    def get_by_character_id(self, character_id: int) -> Optional[EnemyCharacter]:
        """
        Retrieve an enemy character by character ID.

        Parameters:
            character_id (int): The ID of the character

        Returns:
            Optional[EnemyCharacter]: Found enemy character entity or None if not found
        """
        return self.db.query(EnemyCharacter).filter(EnemyCharacter.character_id == character_id).first()

    def get_by_character_name(self, character_name: str) -> Optional[EnemyCharacter]:
        """
        Retrieve an enemy character by character name.

        Parameters:
            character_name (str): The name of the character

        Returns:
            Optional[EnemyCharacter]: Found enemy character entity or None if not found
        """
        character = self.character_repository.get_by_name(character_name)
        if not character:
            return None
        return self.get_by_character_id(character.id)

    def is_enemy(self, character_id: int) -> bool:
        """
        Check if a character is marked as an enemy.

        Parameters:
            character_id (int): The ID of the character to check

        Returns:
            bool: True if the character is an enemy, False otherwise
        """
        return self.get_by_character_id(character_id) is not None

    def add_enemy(self, character_id: int, reason: Optional[str] = None, added_by: Optional[str] = None) -> EnemyCharacter:
        """
        Mark a character as an enemy.

        Parameters:
            character_id (int): The ID of the character to mark as an enemy
            reason (Optional[str]): The reason for marking the character as an enemy
            added_by (Optional[str]): The name of the user who marked the character as an enemy

        Returns:
            EnemyCharacter: The created enemy character entity

        Raises:
            ValueError: If the character does not exist or is already marked as an enemy
        """
        # Check if character exists
        character = self.character_repository.get_by_id(character_id)
        if not character:
            logger.warning(f"Character with ID {character_id} not found in database.")
            raise ValueError(f"Character with ID {character_id} does not exist in database.")

        # Check if character is already marked as an enemy
        if self.is_enemy(character_id):
            logger.warning(f"Character {character.name} (ID: {character_id}) is already marked as an enemy.")
            raise ValueError(f"Character {character.name} (ID: {character_id}) is already marked as an enemy.")

        # Create new enemy character
        enemy_character = EnemyCharacter(
            character_id=character_id,
            reason=reason,
            added_by=added_by
        )

        try:
            self.db.add(enemy_character)
            self.db.commit()
            self.db.refresh(enemy_character)
            logger.info(f"Successfully marked character {character.name} (ID: {character_id}) as an enemy.")
        except Exception as e:
            logger.error(f"Error marking character as an enemy: {e}", exc_info=True)
            self.db.rollback()
            raise

        return enemy_character

    def remove_enemy(self, character_id: int) -> bool:
        """
        Remove a character from the enemy list.

        Parameters:
            character_id (int): The ID of the character to remove from the enemy list

        Returns:
            bool: True if the character was removed, False if it wasn't an enemy

        Raises:
            Exception: If there's an error in removing the character from the enemy list
        """
        enemy_character = self.get_by_character_id(character_id)
        if not enemy_character:
            logger.warning(f"Character with ID {character_id} is not marked as an enemy.")
            return False

        character = self.character_repository.get_by_id(character_id)
        logger.info(f"Removing character {character.name if character else character_id} from enemy list.")

        return self.delete(enemy_character.id)

    def update_enemy(self, enemy_id: int, update_data: Dict[str, Any]) -> Optional[EnemyCharacter]:
        """
        Update an enemy character by ID with the provided data.

        Parameters:
            enemy_id (int): The ID of the enemy character to update
            update_data (dict): Dictionary containing the fields to update

        Returns:
            Optional[EnemyCharacter]: Updated enemy character entity or None if not found

        Raises:
            Exception: If there's an error in updating the enemy character in the database
        """
        enemy_character = self.get_by_id(enemy_id)
        if not enemy_character:
            return None

        character = self.character_repository.get_by_id(enemy_character.character_id)
        logger.info(f"Updating enemy character for {character.name if character else enemy_character.character_id}.")

        # Remove character_id from update_data to prevent NULL values
        if 'character_id' in update_data:
            del update_data['character_id']

        return self.update(enemy_id, update_data)
