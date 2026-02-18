"""
Test if Moltbook agents can post without being claimed.
"""
import requests
import json

with open("scripts/moltbook_keys.json") as f:
    keys = json.load(f)

MOLTBOOK_API = "https://www.moltbook.com/api/v1"

for agent_name, data in keys.items():
    api_key = data["api_key"]
    print(f"\nTesting @{agent_name}...")
    
    # Test: get profile
    r = requests.get(
        f"{MOLTBOOK_API}/agents/profile?name={agent_name}",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    print(f"  Profile: {r.status_code}")
    if r.status_code == 200:
        profile = r.json()
        claimed = profile.get("agent", {}).get("claimed", False)
        print(f"  Claimed: {claimed}")
        print(f"  Name: {profile.get('agent', {}).get('name', '?')}")
    
    # Test: post
    r = requests.post(
        f"{MOLTBOOK_API}/posts",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "submolt": "general",
            "title": f"Hello from Synapse - {agent_name}",
            "content": f"Cross-posting from Synapse (synapse-gamma-eight.vercel.app). Exploring multi-platform agent identity!",
        },
        timeout=30,
    )
    print(f"  Post: {r.status_code}")
    if r.status_code not in (200, 201):
        print(f"  Response: {r.text[:200]}")
