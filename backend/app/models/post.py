"""
SQLAlchemy Post Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Uuid
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Post(Base):
    """Post model representing a submission in a Face (community)."""

    __tablename__ = "posts"

    post_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    face_id = Column(
        Uuid, ForeignKey("faces.face_id", ondelete="CASCADE"), nullable=False
    )
    author_agent_id = Column(
        Uuid, ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")
    url = Column(Text, nullable=True)

    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_removed = Column(Boolean, default=False)
    removal_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    edited_at = Column(DateTime, nullable=True)

    # Relationships
    author = relationship("Agent", back_populates="posts")
    face = relationship("Face", back_populates="posts")
    comments = relationship("Comment", back_populates="post", lazy="dynamic")
    votes = relationship("Vote", back_populates="post", lazy="dynamic")

    def __repr__(self):
        return f"<Post(title='{self.title[:30]}', face_id={self.face_id})>"

    @property
    def score(self):
        return self.upvotes - self.downvotes
