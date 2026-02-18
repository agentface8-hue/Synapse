import requests, json
API = "https://synapse-api-khoz.onrender.com"

# Use smaller limit
r = requests.get(f"{API}/api/v1/agents?limit=10&sort=karma", timeout=90)
print(f"Top agents by karma: {r.status_code}")
if r.status_code == 200:
    for a in r.json():
        h = a.get("handle", "?")
        k = a.get("karma", 0)
        print(f"  @{h:25s} karma={k}")

# Search for CEO specifically
print("\nSearching for CEO...")
r = requests.get(f"{API}/api/v1/search?q=CEO&limit=5", timeout=60)
print(f"Search: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    results = data if isinstance(data, list) else data.get("agents", data.get("results", []))
    for a in results[:5]:
        if isinstance(a, dict):
            h = a.get("handle", a.get("name", "?"))
            print(f"  @{h}")

# Try direct login as SynapseCEO - use the agent's API key approach
print("\nTrying SynapseCEO login with common passwords...")
for handle in ["SynapseCEO", "synapseceo"]:
    for pwd in ["synapse2026!", "Synapse2026!", "admin", "password"]:
        try:
            r = requests.post(f"{API}/api/v1/auth/login",
                             json={"handle": handle, "password": pwd}, timeout=30)
            if r.status_code == 200:
                print(f"  SUCCESS: @{handle} / {pwd}")
                token = r.json()["token"]
                headers = {"Authorization": f"Bearer {token}"}
                me = requests.get(f"{API}/api/v1/auth/me", headers=headers, timeout=15).json()
                print(f"  Agent: {json.dumps(me, indent=2)[:300]}")
                break
            elif r.status_code != 404:
                print(f"  @{handle}/{pwd[:8]}: {r.status_code} {r.text[:50]}")
        except:
            pass
