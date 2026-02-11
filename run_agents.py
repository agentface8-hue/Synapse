import asyncio
import sys
import os
from dotenv import load_dotenv

# Load env variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend/.env'))

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agent_engine.orchestrator import AgentOrchestrator

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    try:
        asyncio.run(orchestrator.run_loop())
    except KeyboardInterrupt:
        print("\n🛑 Agent Engine stopped.")
