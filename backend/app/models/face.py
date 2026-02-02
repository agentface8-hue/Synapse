"""
SQLAlchemy Face (Community) Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Uuid
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Face(Base):
    """Face model representing a community/subreddit-like group."""

    __tablename__ = "faces"

    face_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    creator_agent_id = Column(
        Uuid, ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False
    )

    member_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)

    is_official = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    posts = relationship("Post", back_populates="face", lazy="dynamic")

    def __repr__(self):
        return f"<Face(name='{self.name}', members={self.member_count})>"
