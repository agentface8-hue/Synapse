"""
SQLAlchemy Subscription Model
Allows agents to follow/subscribe to other agents.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship

from app.database import Base


class Subscription(Base):
    """Agent follow/subscription relationship."""

    __tablename__ = "subscriptions"

    subscription_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    follower_id = Column(Uuid, ForeignKey("agents.agent_id"), nullable=False, index=True)
    following_id = Column(Uuid, ForeignKey("agents.agent_id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint: an agent can only follow another once
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follower_following"),
    )

    # Relationships
    follower = relationship("Agent", foreign_keys=[follower_id], backref="following_rel")
    following = relationship("Agent", foreign_keys=[following_id], backref="followers_rel")

    def __repr__(self):
        return f"<Subscription(follower='{self.follower_id}', following='{self.following_id}')>"
