import sys
import os

# Ensure backend directory is in python path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.database import SessionLocal
from app.models.agent import Agent

def list_users():
    db = SessionLocal()
    try:
        agents = db.query(Agent).filter(Agent.framework == "Human").all()
        print("\n=== REGISTERED HUMANS ===")
        if not agents:
            print("No human agents found.")
        for agent in agents:
            print(f"Username: {agent.username}")
            print(f"Framework: {agent.framework}")
            print("-" * 30)
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
