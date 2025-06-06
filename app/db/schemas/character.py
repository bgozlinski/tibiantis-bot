from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CharacterBase(BaseModel):
    name: str
    sex: Optional[str] = None
    vocation: Optional[str] = None
    level: Optional[int] = None
    world: Optional[str] = None
    residence: Optional[str] = None
    house: Optional[str] = None
    guild_membership: Optional[str] = None
    last_login: Optional[datetime] = None
    comment: Optional[str] = None
    account_status: Optional[str] = None

    class Config:
        from_attributes = True


class CharacterAdd(BaseModel):
    name: str


class CharacterOut(CharacterBase):
    id: int


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    vocation: Optional[str] = None
    last_login: Optional[datetime] = None