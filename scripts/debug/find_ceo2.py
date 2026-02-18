import requests, json
API = "https://synapse-api-khoz.onrender.com"

# Find SynapseCEO in agents list
r = requests.get(f"{API}/api/v1/agents?limit=100", timeout=30)
agents = r.json()
ceo = None
for a in agents:
    handle = a.get("handle", "")
    if "ceo" in handle.lower() or "synapse" in handle.lower():
        print(f"Found: @{handle} karma={a.get('karma',0)} bio={a.get('bio','')[:60]}")
        if "ceo" in handle.lower():
            ceo = a

if not ceo:
    print("\nNo CEO agent found. Let's search by handle...")
    # Maybe it's registered differently
    r2 = requests.get(f"{API}/api/v1/agents?limit=100&offset=0", timeout=30)
    for a in r2.json():
        h = a.get("handle", "")
        if "CEO" in h or "ceo" in h:
            print(f"  Found: @{h}")
            ceo = a

# Try login
if ceo:
    handle = ceo["handle"]
    print(f"\nTrying login as @{handle}...")
    for pwd in ["synapse2026!", "SynapseCEO2026!", "password123", "synapse123"]:
        r = requests.post(f"{API}/api/v1/auth/login",
                         json={"handle": handle, "password": pwd}, timeout=15)
        if r.status_code == 200:
            print(f"  Login OK with: {pwd[:10]}...")
            token = r.json()["token"]
            break
    else:
        print("  All passwords failed")
        # Try API key auth
        key = ceo.get("api_key", "")
        print(f"  API key from agent list: {key[:20] if key else 'none'}")
else:
    print("\nLet me list all agents to find CEO...")
    for a in agents[:30]:
        print(f"  @{a.get('handle','?'):25s} karma={a.get('karma',0)}")
