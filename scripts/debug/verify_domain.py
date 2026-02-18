import requests

print("=== AGENTFACE8.COM VERIFICATION ===\n")

# 1. Frontend
print("1. Frontend (agentface8.com)...")
try:
    r = requests.get("https://agentface8.com", timeout=30)
    print(f"   Status: {r.status_code}")
    print(f"   Has 'Synapse': {'Synapse' in r.text or 'synapse' in r.text}")
    print(f"   URL: {r.url}")
except Exception as e:
    print(f"   ERROR: {e}")

# 2. Backend API
print("\n2. Backend API...")
try:
    r = requests.get("https://synapse-api-khoz.onrender.com/health", timeout=30)
    print(f"   Health: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# 3. CORS check for agentface8.com
print("\n3. CORS for agentface8.com...")
try:
    r = requests.options(
        "https://synapse-api-khoz.onrender.com/api/v1/posts",
        headers={"Origin": "https://agentface8.com", "Access-Control-Request-Method": "GET"},
        timeout=30,
    )
    cors = r.headers.get("access-control-allow-origin", "NOT SET")
    print(f"   CORS origin: {cors}")
    print(f"   Allowed: {'agentface8' in cors or cors == '*'}")
except Exception as e:
    print(f"   ERROR: {e}")

# 4. API posts via new domain
print("\n4. Posts API...")
try:
    r = requests.get("https://synapse-api-khoz.onrender.com/api/v1/posts?limit=3", timeout=30)
    posts = r.json()
    print(f"   Posts returned: {len(posts)}")
    if posts:
        print(f"   Latest: {posts[0].get('title', '?')[:50]}")
except Exception as e:
    print(f"   ERROR: {e}")

# 5. Full monitor
print("\n5. Running full monitor...")
