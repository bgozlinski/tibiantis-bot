from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.dependecies import get_db
from app.db.schemas.character import CharacterAdd, CharacterOut, CharacterUpdate
from app.repositories.character_repository import CharacterRepository
from app.scrapers.tibiantis_scraper import TibiantisScraper

router = APIRouter()

@router.get("/", response_model=List[CharacterOut])
async def get_characters(
        db: Session = Depends(get_db)
):
    """
    Get all characters from the database.

    Returns:
        List[CharacterOut]: List of all tracked characters
    """
    repository = CharacterRepository(db)
    return repository.get_all()

@router.get("/{character_id}", response_model=CharacterOut)
async def get_character(
        character_id: int,
        db: Session = Depends(get_db)
):
    """
    Get a character by ID from the database.

    Parameters:
        character_id (int): The ID of the character to retrieve
        db (Session): SQLAlchemy database session object

    Returns:
        CharacterOut: Character data

    Raises:
        HTTPException: If a character with specified ID is not found
    """
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
        character_data: CharacterAdd,
        db: Session = Depends(get_db)
):
    """
    Add an existing character to a tracking database.

    Parameters:
        character_data (CharacterCreate): Character data schema instance
        db (Session): SQLAlchemy database session object

    Returns:
        Character: Tracked character entity

    Example:
        repo = CharacterRepository(db_session)
        tracking_data = CharacterCreate(name="John Doe", last_seen_location="Thais")
        tracked_character = repo.add_character_to_tracking(tracking_data)
    """
    repository = CharacterRepository(db)

    if repository.exists_by_name(character_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Character with name: {character_data.name} already exists"
        )

    try:
        character = repository.add_by_name(character_data.name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not retrieve character data from Tibiantis Online: {str(e)}"
        )

    return character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
        character_id: int,
        db: Session = Depends(get_db)
):
    """
    Delete a character by ID from the database.

    Parameters:
        character_id (int): The ID of the character to delete
        db (Session): SQLAlchemy database session object

    Raises:
        HTTPException: If a character with specified ID is not found
    """
    repository = CharacterRepository(db)
    character = repository.get_by_id(character_id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    repository.delete_character_by_id(character_id)

@router.get("/info/{character_name}")
async def get_character_info(
        character_name: str
):
    """
    Get character information directly from Tibiantis Online.

    This endpoint scrapes character data from the Tibiantis website without
    adding the character to the tracking database.

    Parameters:
        character_name (str): The name of the character to retrieve information for

    Returns:
        dict: Character data scraped from Tibiantis Online

    Raises:
        HTTPException: If a character with a specified name is not found on Tibiantis Online
    """
    scraper = TibiantisScraper()
    character_data = scraper.get_character_data(character_name)
    if character_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with name: {character_name} not found"
        )
    return character_data


@router.patch("/{character_id}", response_model=CharacterOut)
async def update_character(
        character_id: int,
        character_data: CharacterUpdate,
        db: Session = Depends(get_db)
):
    """
    Update a character's name and/or last seen location by ID.

    This endpoint allows updating either the name, the last seen location, or both
    for a character identified by ID.

    Parameters:
        character_id (int): The ID of the character to update
        character_data (CharacterUpdate): Data containing fields to update
        db (Session): SQLAlchemy database session object

    Returns:
        CharacterOut: Updated character data

    Raises:
        HTTPException: If a character with specified ID is not found, or update fails
    """
    repository = CharacterRepository(db)

    if not repository.get_by_id(character_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id: {character_id} not found"
        )

    try:
        update_data = {k: v for k, v in character_data.model_dump().items() if v is not None}

        if not update_data:
            return repository.get_by_id(character_id)

        character = repository.update_character_by_id(character_id, update_data)
        return character
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not update character: {str(e)}"
        )
