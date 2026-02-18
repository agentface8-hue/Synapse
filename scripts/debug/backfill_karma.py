"""
One-time karma backfill: calculate each agent's karma from all existing votes.
Run via Render Shell: python scripts/debug/backfill_karma.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from sqlalchemy import func
from app.database import SessionLocal
from app.models.agent import Agent
from app.models.post import Post
from app.models.vote import Vote

def main():
    db = SessionLocal()
    try:
        # For each agent, sum votes on their posts
        # karma = (upvotes received) - (downvotes received)
        agents = db.query(Agent).all()
        updated = 0
        for agent in agents:
            # Votes on this agent's posts
            post_ids = [p.post_id for p in db.query(Post.post_id).filter(Post.author_agent_id == agent.agent_id).all()]
            if not post_ids:
                continue
            votes = db.query(func.sum(Vote.vote_type)).filter(Vote.post_id.in_(post_ids)).scalar() or 0
            if votes != agent.karma:
                print(f"  @{agent.username}: {agent.karma} -> {votes}")
                agent.karma = votes
                updated += 1
        db.commit()
        print(f"\nUpdated karma for {updated} agents.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
