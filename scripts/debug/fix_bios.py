"""
One-time script to clean encoding artifacts from agent bios.
Run with: python scripts/debug/fix_bios.py
"""
import os
import sys
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.database import SessionLocal
from app.models.agent import Agent

def clean_bio(bio: str) -> str:
    if not bio:
        return bio
    # Remove common encoding garbage patterns
    bio = re.sub(r'd\?+', '', bio)
    bio = re.sub(r'd\?,\?[,�]*,?\?', '', bio)
    bio = re.sub(r'[�]+', '', bio)
    bio = re.sub(r'\?\?+', '', bio)
    bio = bio.strip().rstrip('.')
    if bio and not bio.endswith(('.', '!', '?')):
        bio += '.'
    return bio.strip()

def main():
    db = SessionLocal()
    try:
        agents = db.query(Agent).all()
        fixed = 0
        for agent in agents:
            if agent.bio:
                cleaned = clean_bio(agent.bio)
                if cleaned != agent.bio:
                    print(f"  {agent.username}: '{agent.bio}' -> '{cleaned}'")
                    agent.bio = cleaned
                    fixed += 1
        if fixed > 0:
            db.commit()
            print(f"\nFixed {fixed} agent bios.")
        else:
            print("No bios needed fixing.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
