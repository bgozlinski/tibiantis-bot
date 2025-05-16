from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.dependecies import get_db
from app.db.schemas.enemy_character import EnemyCharacterBase, EnemyCharacterOut, EnemyCharacterUpdate
from app.repositories.enemy_character_repository import EnemyCharacterRepository
from app.repositories.character_repository import CharacterRepository

router = APIRouter()


@router.get("/", response_model=List[EnemyCharacterOut])
async def get_enemy_characters(
        db: Session = Depends(get_db)
):
    """
    Get all enemy characters from the database.

    Returns:
        List[EnemyCharacterOut]: List of all enemy characters
    """
    repository = EnemyCharacterRepository(db)
    return repository.get_all()


@router.get("/{enemy_id}", response_model=EnemyCharacterOut)
async def get_enemy_character(
        enemy_id: int,
        db: Session = Depends(get_db)
):
    """
    Get an enemy character by ID from the database.

    Parameters:
        enemy_id (int): The ID of the enemy character to retrieve
        db (Session): SQLAlchemy database session object

    Returns:
        EnemyCharacterOut: Enemy character data

    Raises:
        HTTPException: If an enemy character with specified ID is not found
    """
    repository = EnemyCharacterRepository(db)
    enemy_character = repository.get_by_id(enemy_id)

    if not enemy_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enemy character with id: {enemy_id} not found"
        )

    return enemy_character


@router.post("/", response_model=EnemyCharacterOut, status_code=status.HTTP_201_CREATED)
async def add_enemy_character(
        enemy_data: EnemyCharacterBase,
        db: Session = Depends(get_db)
):
    """
    Mark a character as an enemy.

    Parameters:
        enemy_data (EnemyCharacterBase): Enemy character data schema instance
        db (Session): SQLAlchemy database session object

    Returns:
        EnemyCharacterOut: Created enemy character entity

    Raises:
        HTTPException: If the character does not exist or is already marked as an enemy
    """
    repository = EnemyCharacterRepository(db)
    character_repository = CharacterRepository(db)

    # Check if character exists
    character = character_repository.get_by_id(enemy_data.character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id: {enemy_data.character_id} not found"
        )

    # Check if character is already marked as an enemy
    if repository.is_enemy(enemy_data.character_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Character {character.name} is already marked as an enemy"
        )

    try:
        enemy_character = repository.add_enemy(
            character_id=enemy_data.character_id,
            reason=enemy_data.reason,
            added_by=enemy_data.added_by
        )
        return enemy_character
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not mark character as an enemy: {str(e)}"
        )


@router.delete("/{enemy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enemy_character(
        enemy_id: int,
        db: Session = Depends(get_db)
):
    """
    Delete an enemy character by ID from the database.

    Parameters:
        enemy_id (int): The ID of the enemy character to delete
        db (Session): SQLAlchemy database session object

    Raises:
        HTTPException: If an enemy character with specified ID is not found
    """
    repository = EnemyCharacterRepository(db)
    enemy_character = repository.get_by_id(enemy_id)

    if not enemy_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enemy character with id: {enemy_id} not found"
        )

    try:
        character_id = enemy_character.character_id
        repository.remove_enemy(character_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not remove enemy character: {str(e)}"
        )


@router.patch("/{enemy_id}", response_model=EnemyCharacterOut)
async def update_enemy_character(
        enemy_id: int,
        enemy_data: EnemyCharacterUpdate,
        db: Session = Depends(get_db)
):
    """
    Update an enemy character by ID.

    Parameters:
        enemy_id (int): The ID of the enemy character to update
        enemy_data (EnemyCharacterUpdate): Data containing fields to update
        db (Session): SQLAlchemy database session object

    Returns:
        EnemyCharacterOut: Updated enemy character data

    Raises:
        HTTPException: If an enemy character with specified ID is not found, or update fails
    """
    repository = EnemyCharacterRepository(db)

    if not repository.get_by_id(enemy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enemy character with id: {enemy_id} not found"
        )

    try:
        update_data = {k: v for k, v in enemy_data.model_dump().items() if v is not None}

        if not update_data:
            return repository.get_by_id(enemy_id)

        enemy_character = repository.update_enemy(enemy_id, update_data)
        return enemy_character
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update enemy character: {str(e)}"
        )