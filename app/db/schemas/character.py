from pydantic import BaseModel


class CharacterBase(BaseModel):
    name: str


class CharacterCreate(CharacterBase):
    ...


class CharacterOut(CharacterBase):
    id: int
