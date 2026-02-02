"""
SQLAlchemy Audit Log Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON, Uuid
# from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class AuditLog(Base):
    """Audit log for tracking security-relevant events."""

    __tablename__ = "audit_log"

    log_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    agent_id = Column(
        Uuid, ForeignKey("agents.agent_id", ondelete="SET NULL"), nullable=True
    )

    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Uuid, nullable=True)

    metadata_ = Column("metadata", JSON, nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', agent={self.agent_id})>"
