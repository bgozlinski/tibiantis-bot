from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EnemyCharacterBase(BaseModel):
    character_id: int
    reason: Optional[str] = None
    added_by: Optional[str] = None

    class Config:
        from_attributes = True


class EnemyCharacterCreate(EnemyCharacterBase):
    pass


class EnemyCharacterOut(EnemyCharacterBase):
    id: int
    created_at: datetime
    updated_at: datetime


class EnemyCharacterUpdate(BaseModel):
    reason: Optional[str] = None
    added_by: Optional[str] = None