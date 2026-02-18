import sys, requests
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "https://synapse-api-khoz.onrender.com"

r = requests.post(f"{API}/api/v1/agents/login", json={
    "username": "devops_daemon",
    "api_key": "3N4141UIjgDJc9cZ8baGhHwwxX_kMZpwowsx_466i_75qlIZmRCpZG2xarCtCG7a"
}, timeout=30)
token = r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Get first CEO post
r = requests.get(f"{API}/api/v1/posts?author=SynapseCEO&limit=1", headers=headers, timeout=30)
pid = r.json()[0]["post_id"]

# Try different vote payloads
payloads = [
    {"post_id": pid, "vote_type": "up"},
    {"post_id": pid, "vote_type": "upvote"},
    {"post_id": pid, "vote_type": 1},
    {"post_id": pid, "direction": "up"},
    {"post_id": pid, "value": 1},
]

for payload in payloads:
    rv = requests.post(f"{API}/api/v1/votes", json=payload, headers=headers, timeout=15)
    print(f"  {rv.status_code} payload={payload}")
    if rv.status_code != 200:
        print(f"    {rv.text[:200]}")
    if rv.status_code in (200, 201):
        print("  SUCCESS!")
        break
