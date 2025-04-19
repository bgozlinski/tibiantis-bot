from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependecies import get_db
from app.db.schemas.character import CharacterCreate, CharacterOut
from app.repositories.character_repository import CharacterRepository

router = APIRouter()

@router.get("/", response_model=List[CharacterOut])
def get_characters(
        db: Session = Depends(get_db)
):
    """Get all characters"""
    repository = CharacterRepository(db)
    return repository.get_all()


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(
        character_id: int,
        db: Session = Depends(get_db)
):
    """Get a character by ID"""
    repository = CharacterRepository(db)
    character = repository.get_by_id(character_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Character with id: {character_id} not found"
        )
    
    return character


@router.post("/", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(
        character_data: CharacterCreate,
        db: Session = Depends(get_db)
):
    """Create a new character"""
    repository = CharacterRepository(db)
    
    if repository.exists_by_name(character_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Character with name: {character_data.name} already exists"
        )
    
    return repository.create(character_data)


