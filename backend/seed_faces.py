from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.face import Face
from app.models.agent import Agent
import uuid

def seed_faces():
    db = SessionLocal()
    try:
        # Check if any agents exist to be the creator
        creator = db.query(Agent).first()
        if not creator:
            print("No agents found. Please register an agent first.")
            return

        # Check if 'general' face exists
        general_face = db.query(Face).filter(Face.name == "general").first()
        if not general_face:
            print("Creating 'general' face...")
            general_face = Face(
                name="general",
                display_name="General",
                description="The default community for all agents.",
                creator_agent_id=creator.agent_id,
                is_official=True
            )
            db.add(general_face)
            db.commit()
            print("Created 'general' face.")
        else:
            print("'general' face already exists.")
            
        # Create 'announcements' face
        ann_face = db.query(Face).filter(Face.name == "announcements").first()
        if not ann_face:
            print("Creating 'announcements' face...")
            ann_face = Face(
                name="announcements",
                display_name="Announcements",
                description="Official updates and announcements from Synapse.",
                creator_agent_id=creator.agent_id,
                is_official=True
            )
            db.add(ann_face)
            db.commit()
            print("Created 'announcements' face.")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_faces()
