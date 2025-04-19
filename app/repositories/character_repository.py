from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.models.character import Character
from app.db.schemas.character import CharacterCreate

class CharacterRepository:
    """Repository for Character model operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Character]:
        """Get all characters"""
        return self.db.query(Character).all()
    
    def get_by_id(self, character_id: int) -> Optional[Character]:
        """Get character by ID"""
        return self.db.query(Character).filter(Character.id == character_id).first()
    
    def exists_by_name(self, name: str) -> bool:
        """Check if character with given name exists"""
        return self.db.query(Character).filter(Character.name == name).first() is not None
    
    def create(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        character = Character(**character_data.model_dump())
        
        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)
        
        return character
