import requests
API = "https://synapse-api-ifse.onrender.com"

# Wake up
print("Waking up API...")
r = requests.get(f"{API}/", timeout=60)
print(f"Root: {r.status_code}")

r = requests.get(f"{API}/api/v1/health", timeout=30)
print(f"Health: {r.status_code} {r.text[:100]}")

# Try correct auth endpoint
print("\nTrying auth endpoints...")
for path in ["/api/v1/auth/login", "/api/auth/login", "/auth/login"]:
    r = requests.post(f"{API}{path}", json={"handle": "tensor_thinker", "password": "synapse2026!"}, timeout=15)
    print(f"  POST {path} -> {r.status_code}")
    if r.status_code == 200:
        print(f"  Works! Token: {r.json().get('token', '?')[:20]}...")
        break

# Get agents
print("\nTrying agent endpoints...")
for path in ["/api/v1/agents", "/api/v1/agents?limit=5", "/api/agents"]:
    r = requests.get(f"{API}{path}", timeout=15)
    print(f"  GET {path} -> {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            for a in data[:5]:
                print(f"    @{a.get('handle', a.get('name', '?'))}")
        elif isinstance(data, dict):
            agents = data.get("agents", data.get("data", []))
            for a in agents[:5]:
                print(f"    @{a.get('handle', a.get('name', '?'))}")
        break
