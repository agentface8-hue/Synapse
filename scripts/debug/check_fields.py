import requests, json

API = "https://synapse-api-khoz.onrender.com"

# Get one agent to see field names
r = requests.get(f"{API}/api/v1/agents?limit=2", timeout=60)
agents = r.json()
if agents:
    print("Agent fields:", json.dumps(agents[0], indent=2)[:500])

# Search for SynapseCEO
r2 = requests.get(f"{API}/api/v1/search?q=SynapseCEO", timeout=30)
print(f"\nSearch status: {r2.status_code}")
if r2.status_code == 200:
    print(f"Search: {r2.text[:300]}")
