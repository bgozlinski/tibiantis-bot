from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.schemas.character import CharacterCreate, CharacterOut
from app.db.session import SessionLocal
from app.db.models.character import Character

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[CharacterOut])
def get_characters(
        db: Session = Depends(get_db)
):
    return db.query(Character).all()


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(
        character_id: int,
        db: Session = Depends(get_db)
):
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail=f"Character with id:{character_id} not found")
    return character

@router.post("/", response_model=CharacterOut)
def post_character(
        character: CharacterCreate,
        db: Session = Depends(get_db)
):
    character = Character(**character.model_dump())

    if db.query(Character).filter(Character.name == character.name).first():
        raise HTTPException(status_code=400, detail=f"Character with name:{character.name} already exists")

    db.add(character)
    db.commit()
    db.refresh(character)

    return character


