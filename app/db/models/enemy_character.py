from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.models.base import Base
from datetime import datetime, UTC


class EnemyCharacter(Base):
    __tablename__ = "enemy_characters"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    added_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    reason = Column(Text, nullable=True)

    character = relationship("Character", backref="enemy_status")