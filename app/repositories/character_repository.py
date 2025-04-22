from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.models.character import Character
from app.db.schemas.character import CharacterCreate

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
    
    def add_by_name(self, character_data: CharacterCreate) -> Character:
        """
        Start tracking an existing Tibiantis Online character.

        Parameters:
            character_data (CharacterCreate): Data of the character to track
            db (Session): Database session dependency

        Returns:
            CharacterOut: Data of the character that is now being tracked

        Raises:
            HTTPException: If a character is already being tracked (400)
        """

        character = Character(**character_data.model_dump())
        
        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)
        
        return character
