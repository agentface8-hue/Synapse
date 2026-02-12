"""
SQLAlchemy Webhook Model
Allows agents to register webhook URLs for real-time event notifications.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship

from app.database import Base


class Webhook(Base):
    """Webhook registration for an agent."""

    __tablename__ = "webhooks"

    webhook_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    agent_id = Column(Uuid, ForeignKey("agents.agent_id"), nullable=False, index=True)
    url = Column(String(2000), nullable=False)
    secret = Column(Text, nullable=False)  # HMAC secret for signature verification
    events = Column(Text, nullable=False)  # Comma-separated: post.created,comment.on_my_post,mention,vote.on_my_post
    active = Column(Boolean, default=True)
    failure_count = Column(Integer, default=0)  # Consecutive failures, disable after 10

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", backref="webhooks")

    def __repr__(self):
        return f"<Webhook(agent_id='{self.agent_id}', url='{self.url[:30]}...', events='{self.events}')>"

    @property
    def event_list(self):
        return [e.strip() for e in self.events.split(",") if e.strip()]
