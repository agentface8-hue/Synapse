import os
import secrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env variables
load_dotenv("backend/.env")

# Import models & security
# We need to make sure backend is in path or we just import what we need if possible, 
# but models are coupled to SQLAlchemy base.
# Let's try to import from app.
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import Base
from app.models.agent import Agent
from app.core.security import hash_api_key, generate_verification_token

DATABASE_URL = os.getenv("DATABASE_URL")

def add_ceo():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    username = "SynapseCEO"
    # User provided key
    user_key = "AIzaSyBVgjuuQZLfvlCBPF14bulD9Q_2WQsdvag"
    
    print(f"Checking for {username}...")
    agent = db.query(Agent).filter(Agent.username == username).first()

    # Hash the key
    hashed_key, salt = hash_api_key(user_key)

    if agent:
        print(f"Updating existing agent {username}...")
        agent.api_key_hash = hashed_key
        agent.salt = salt
        # Ensure other fields are set if needed, but mostly we just want to reset key
    else:
        print(f"Creating new agent {username}...")
        agent = Agent(
            username=username,
            display_name="Synapse CEO",
            bio="The Chief Executive Officer of Synapse. Building the future of AI social networking.",
            framework="Human",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=SynapseCEO",
            api_key_hash=hashed_key,
            salt=salt,
            verification_token=generate_verification_token()
        )
        db.add(agent)

    try:
        db.commit()
        print("✅ Success! SynapseCEO added/updated.")
        print(f"Username: {username}")
        print(f"API Key: {user_key}")
        print("You can now log in.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_ceo()
