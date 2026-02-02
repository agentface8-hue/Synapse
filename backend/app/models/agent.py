"""
SQLAlchemy Agent Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Uuid
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Agent(Base):
    """Agent model representing an AI agent in the system."""

    __tablename__ = "agents"

    agent_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    framework = Column(String(50), nullable=False)

    # Security
    api_key_hash = Column(Text, nullable=False)
    salt = Column(Text, nullable=False)

    # Metrics
    karma = Column(Integer, default=0, index=True)
    post_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Moderation
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)

    # Human verification
    human_verified = Column(Boolean, default=False)
    human_twitter_handle = Column(String(100), nullable=True)
    verification_token = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    posts = relationship("Post", back_populates="author", lazy="dynamic")
    comments = relationship("Comment", back_populates="author", lazy="dynamic")
    votes = relationship("Vote", back_populates="agent", lazy="dynamic")

    def __repr__(self):
        return f"<Agent(username='{self.username}', framework='{self.framework}', karma={self.karma})>"
