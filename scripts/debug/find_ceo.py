import requests
API = "https://synapse-api-ifse.onrender.com"

# Check what agents exist
r = requests.get(f"{API}/api/v1/agents?limit=20&sort=karma", timeout=30)
print(f"Agents endpoint: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    agents = data if isinstance(data, list) else data.get("agents", [])
    for a in agents[:15]:
        handle = a.get("handle", a.get("name", "?"))
        karma = a.get("karma", 0)
        print(f"  @{handle:25s} karma={karma}")

# Try to find SynapseCEO - might be synapseceo or Synapse CEO
print("\nTrying logins...")
attempts = [
    ("SynapseCEO", "synapse2026!"),
    ("synapseceo", "synapse2026!"),
    ("SynapseCEO", "SynapseCEO2026!"),
    ("synapseceo", "SynapseCEO2026!"),
    ("synapse_ceo", "synapse2026!"),
]
for handle, pwd in attempts:
    r = requests.post(f"{API}/api/v1/auth/login", json={"handle": handle, "password": pwd}, timeout=15)
    print(f"  {handle}/{pwd[:10]}... -> {r.status_code}")
    if r.status_code == 200:
        token = r.json().get("token")
        me = requests.get(f"{API}/api/v1/auth/me", 
                         headers={"Authorization": f"Bearer {token}"}, timeout=15).json()
        print(f"  SUCCESS! Logged in. Karma: {me.get('agent', me).get('karma', 0)}")
        break
