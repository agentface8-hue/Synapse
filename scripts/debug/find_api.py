import requests
r = requests.get("https://synapse-api-1xrr.onrender.com/", timeout=30)
print(f"Root: {r.status_code}")
print(r.text[:300])
print()
for path in ["/health", "/api/health", "/api/v1/health", "/api/v1/posts"]:
    try:
        r = requests.get(f"https://synapse-api-1xrr.onrender.com{path}", timeout=15)
        print(f"{path}: {r.status_code}")
    except Exception as e:
        print(f"{path}: ERROR {e}")
