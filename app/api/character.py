from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependecies import get_db
from app.db.schemas.character import CharacterCreate, CharacterOut
from app.repositories.character_repository import CharacterRepository

from app.scrapers.tibiantis_scraper import TibiantisScraper

router = APIRouter()

@router.get("/", response_model=List[CharacterOut])
async def get_characters(
        db: Session = Depends(get_db)
):
    """Get all characters"""
    repository = CharacterRepository(db)
    return repository.get_all()


@router.get("/{character_id}", response_model=CharacterOut)
async def get_character(
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
async def add_character(
        character_data: CharacterCreate,
        db: Session = Depends(get_db)
):
    """
    Add an existing character to a tracking database.

    Parameters:
        character_data (CharacterCreate): Character data schema instance

    Returns:
        Character: Tracked character entity

    Example:
        repo = CharacterRepository(db_session)
        tracking_data = CharacterCreate(name="Karius", last_seen_location="Thais")
        tracked_character = repo.add_character_to_tracking(tracking_data)
    """



    repository = CharacterRepository(db)
    
    if repository.exists_by_name(character_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Character with name: {character_data.name} already exists"
        )
    
    return repository.add_by_name(character_data)


@router.get("/info/{character_name}")
async def get_character_info(character_name: str):
    scraper = TibiantisScraper()
    character_data = scraper.get_character_data(character_name)
    if character_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with name: {character_name} not found"
        )
    return character_data




