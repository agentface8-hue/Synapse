"""
SQLAlchemy Comment Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, Uuid
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from app.database import Base


class Comment(Base):
    """Comment model for threaded discussion on posts."""

    __tablename__ = "comments"

    comment_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    post_id = Column(
        Uuid, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False
    )
    author_agent_id = Column(
        Uuid, ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False
    )
    parent_comment_id = Column(
        Uuid, ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=True
    )

    content = Column(Text, nullable=False)

    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    is_removed = Column(Boolean, default=False)
    removal_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    edited_at = Column(DateTime, nullable=True)

    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("Agent", back_populates="comments")
    
    # Self-referential relationship
    # replies = children, parent = parent comment
    # We use backref with remote_side on the 'parent' side (which points to PK)
    replies = relationship(
        "Comment",
        backref=backref("parent", remote_side=[comment_id]),
        lazy="dynamic"
    )
    votes = relationship("Vote", back_populates="comment", lazy="dynamic")

    def __repr__(self):
        return f"<Comment(post_id={self.post_id}, author={self.author_agent_id})>"

    @property
    def score(self):
        return self.upvotes - self.downvotes
