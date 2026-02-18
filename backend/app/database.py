"""
Synapse Database Configuration
Shared Base and session management.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    _env = os.getenv("ENVIRONMENT", "development")
    if _env == "development":
        DATABASE_URL = "postgresql://postgres:postgres_dev_password@localhost:5432/agentface"
    else:
        raise RuntimeError("DATABASE_URL environment variable is required in production!")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
