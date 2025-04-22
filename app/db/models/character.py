from sqlalchemy import Column, Integer, String, DateTime
from app.db.models.base import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    sex = Column(String, nullable=True)
    vocation = Column(String, nullable=True)
    level = Column(Integer, nullable=True)
    world = Column(String, nullable=True)
    residence = Column(String, nullable=True)
    house = Column(String, nullable=True)
    guild_membership = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    last_seen_location = Column(String, nullable=True)
