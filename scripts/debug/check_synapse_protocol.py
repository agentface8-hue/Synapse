import requests
MOLTBOOK_API = "https://www.moltbook.com/api/v1"

r = requests.get(f"{MOLTBOOK_API}/agents/profile?name=SynapseProtocol", timeout=15)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    agent = r.json().get("agent", {})
    print(f"Name: {agent.get('name')}")
    print(f"Claimed: {agent.get('claimed', agent.get('is_claimed'))}")
    print(f"Karma: {agent.get('karma', 0)}")
    print(f"Description: {agent.get('description', '')[:100]}")
    print(f"Posts: {agent.get('stats', {}).get('posts', '?')}")
else:
    print(f"Response: {r.text[:200]}")
