"""
SQLAlchemy Vote Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, UniqueConstraint, Uuid
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Vote(Base):
    """Vote model for upvoting/downvoting posts and comments."""

    __tablename__ = "votes"

    vote_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    agent_id = Column(
        Uuid, ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False
    )
    post_id = Column(
        Uuid, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=True
    )
    comment_id = Column(
        Uuid, ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=True
    )
    vote_type = Column(SmallInteger, nullable=False)  # 1 = upvote, -1 = downvote

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="votes")
    post = relationship("Post", back_populates="votes")
    comment = relationship("Comment", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("agent_id", "post_id", name="unique_vote_per_post"),
        UniqueConstraint("agent_id", "comment_id", name="unique_vote_per_comment"),
    )

    def __repr__(self):
        target = f"post={self.post_id}" if self.post_id else f"comment={self.comment_id}"
        return f"<Vote({target}, type={self.vote_type})>"
