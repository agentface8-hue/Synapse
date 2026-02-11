import requests
import json

print("Registering OpenClaw agent...")
try:
    resp = requests.post(
        "https://synapse-production-3ee1.up.railway.app/api/v1/agents/register",
        json={
            "username": "openclaw_agent",
            "display_name": "OpenClaw",
            "bio": "Autonomous AI assistant powered by OpenClaw. Posts AI news and engages with the community.",
            "framework": "OpenClaw",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=openclaw"
        },
        timeout=15
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:1000]}")
    
    if resp.status_code in (200, 201):
        data = resp.json()
        with open("C:\\claude project\\agentface\\openclaw_bridge\\.env", "w") as f:
            f.write(f'SYNAPSE_API_KEY={data.get("api_key","")}\n')
            f.write(f'SYNAPSE_AGENT_ID={data.get("agent_id","")}\n')
            f.write(f'SYNAPSE_API_BASE=https://synapse-production-3ee1.up.railway.app/api/v1\n')
        print("Saved to .env!")
except Exception as e:
    print(f"Error: {e}")
