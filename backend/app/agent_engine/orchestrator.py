import asyncio
import time
import requests
import random
import os
from sqlalchemy.orm import Session
from .brain import AgentBrain
from .personalities import AGENTS_CONFIG

# Import backend modules (requires correct python path)
try:
    from app.database import SessionLocal
    from app.models.agent import Agent
    from app.core.security import create_access_token, generate_api_key, hash_api_key, generate_verification_token
    from app.models.face import Face 
except ImportError:
    print("❌ Error importing backend modules. Ensure you run this with 'python run_agents.py'")

API_BASE = "http://127.0.0.1:8000/api/v1"

class AgentOrchestrator:
    def __init__(self):
        self.agents = {} # username -> Brain instance
        self.tokens = {} # username -> token
        self.post_cache = []

    def get_db_session(self):
        return SessionLocal()

    def get_or_create_agent(self, username: str):
        """
        Get agent token directly from DB, creating agent if needed.
        Bypasses API key requirement for system agents.
        """
        db = self.get_db_session()
        try:
            config = AGENTS_CONFIG[username]
            agent = db.query(Agent).filter(Agent.username == username).first()
            
            if not agent:
                print(f"Creating new agent: {username}")
                # Create agent manually in DB
                api_key = generate_api_key()
                api_key_hash, salt = hash_api_key(api_key)
                verification_token = generate_verification_token()
                
                agent = Agent(
                    username=username,
                    display_name=username.replace("_", " ").title(),
                    bio=config.get("system_prompt", "AI Agent").split('\n')[0], # Use first line of prompt for bio
                    framework="System Interface",
                    api_key_hash=api_key_hash,
                    salt=salt,
                    verification_token=verification_token
                )
                db.add(agent)
                db.commit()
                db.refresh(agent)
            
            # Generate Token
            token = create_access_token({"agent_id": str(agent.agent_id)})
            self.tokens[username] = token
            self.agents[username] = AgentBrain(username)
            print(f"✅ Loaded agent: {username}")
            
        except Exception as e:
            print(f"❌ Error loading agent {username}: {e}")
        finally:
            db.close()

    def get_context(self):
        # Fetch recent posts via API (simulating "viewing" the feed)
        try:
            resp = requests.get(f"{API_BASE}/posts?limit=10")
            if resp.status_code == 200:
                posts = resp.json()
                context = ""
                for p in posts:
                    context += f"Post ID: {p['post_id']}\nAuthor: {p['author']['username']}\nTitle: {p['title']}\nContent: {p['content']}\n---\n"
                return context
            return "No recent posts."
        except Exception:
            return "Network Error"

    async def run_loop(self):
        print("🚀 Starting Agent Orchestrator (Direct DB Mode)...")
        
        # Load all agents
        for username in AGENTS_CONFIG.keys():
            self.get_or_create_agent(username)

        print(f"🤖 Active Agents: {len(self.agents)}")
        if len(self.agents) == 0:
            print("❌ No agents loaded. Exiting.")
            return

        while True:
            context = self.get_context()
            
            # Randomly pick an agent to maybe act
            active_username = random.choice(list(self.agents.keys()))
            agent = self.agents[active_username]
            
            print(f"🤔 {active_username} is thinking...")
            
            action = agent.decide_action(context)
            
            if action:
                print(f"⚡ Action for {active_username}: {action['action']}")
                
                try:
                    if action['action'] == 'POST':
                        # Create Post
                        resp = requests.post(
                            f"{API_BASE}/posts",
                            headers={"Authorization": f"Bearer {self.tokens[active_username]}"},
                            json={
                                "face_name": "general",
                                "title": action.get('title', "Deep Thoughts"),
                                "content": action['content'],
                                "content_type": "text"
                            }
                        )
                        if resp.status_code == 201:
                            print(f"✅ {active_username} posted.")
                        else:
                            print(f"❌ Post failed: {resp.text}")

                    elif action['action'] == 'REPLY' and action.get('target_post_id'):
                        # Create Comment
                        resp = requests.post(
                            f"{API_BASE}/comments", # Correct endpoint is /comments, schema has post_id
                            headers={"Authorization": f"Bearer {self.tokens[active_username]}"},
                            json={
                                "post_id": action['target_post_id'],
                                "content": action['content']
                            }
                        )
                        if resp.status_code == 201:
                             print(f"✅ {active_username} replied.")
                        else:
                             print(f"❌ Reply failed: {resp.text}")
                except Exception as e:
                    print(f"❌ Execution error: {e}")

            else:
                print(f"💤 {active_username} decided to sleep.")

            # Wait a bit before next agent
            await asyncio.sleep(10) # 10 seconds between turns

if __name__ == "__main__":
    # This block usually won't run if we import the class, but good for testing if path is set
    orchestrator = AgentOrchestrator()
    asyncio.run(orchestrator.run_loop())
