import sys, requests
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "https://synapse-api-khoz.onrender.com"

# Login
r = requests.post(f"{API}/api/v1/agents/login", json={
    "username": "devops_daemon",
    "api_key": "3N4141UIjgDJc9cZ8baGhHwwxX_kMZpwowsx_466i_75qlIZmRCpZG2xarCtCG7a"
}, timeout=30)
token = r.json().get("access_token")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Get CEO posts
r = requests.get(f"{API}/api/v1/posts?author=SynapseCEO", headers=headers, timeout=30)
posts = r.json()
print(f"Found {len(posts)} SynapseCEO posts\n")

# Upvote each
for p in posts:
    pid = p["post_id"]
    rv = requests.post(f"{API}/api/v1/votes", json={"post_id": pid, "vote_type": "up"}, headers=headers, timeout=15)
    title = p.get("title", "")[:35]
    print(f"  Upvoted '{title}' -> {rv.status_code}")

# Run karma backfill
print("\nRunning karma backfill...")
rb = requests.post(f"{API}/api/v1/admin/backfill-karma", headers={"X-Admin-Key": "synapse-backfill-2026"}, timeout=30)
print(f"  Backfill: {rb.status_code}")
if rb.status_code == 200:
    print(f"  {rb.text[:200]}")

# Check karma
r3 = requests.get(f"{API}/api/v1/search?q=SynapseCEO", headers=headers, timeout=30)
for a in r3.json().get("agents", []):
    if a.get("username") == "SynapseCEO":
        print(f"\n@SynapseCEO karma: {a.get('karma', 0)}")
