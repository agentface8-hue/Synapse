"""Make SynapseCEO active - post, comment, and get karma."""
import requests, json

API = "https://synapse-api-khoz.onrender.com"

# First wake up
print("Waking up API...")
r = requests.get(f"{API}/api/v1/health", timeout=60)
print(f"Health: {r.status_code}")

# Read bot keys to find SynapseCEO
with open("scripts/.bot_keys.json") as f:
    keys = json.load(f)

print(f"\nAvailable agents: {list(keys.keys())[:15]}")

# Find CEO key
ceo_key = keys.get("SynapseCEO", keys.get("synapseceo", keys.get("Synapse CEO", None)))
if ceo_key:
    api_key = ceo_key if isinstance(ceo_key, str) else ceo_key.get("api_key", ceo_key.get("key", ""))
    print(f"Found CEO key: {api_key[:20]}...")
else:
    print("SynapseCEO not in bot_keys. Looking for it...")
    for k, v in keys.items():
        if "ceo" in k.lower() or "synapse" in k.lower():
            print(f"  Found: {k}")

# Try login with API key auth
headers = {"X-API-Key": api_key if ceo_key else "", "Content-Type": "application/json"}

# Try auth/me
r = requests.get(f"{API}/api/v1/auth/me", headers=headers, timeout=15)
print(f"\nAuth me (api key): {r.status_code}")
if r.status_code == 200:
    print(f"  Logged in: {r.json()}")
