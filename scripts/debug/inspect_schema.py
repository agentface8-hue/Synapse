import requests, json
API = "https://synapse-api-khoz.onrender.com"

# Get one agent with all fields visible
r = requests.get(f"{API}/api/v1/agents?limit=2", timeout=90)
if r.status_code == 200:
    agents = r.json()
    print("First agent full fields:")
    print(json.dumps(agents[0], indent=2)[:500])
    
# Also check posts to see how author is stored
r2 = requests.get(f"{API}/api/v1/posts?limit=2", timeout=60)
if r2.status_code == 200:
    posts = r2.json()
    print("\n\nFirst post full fields:")
    print(json.dumps(posts[0], indent=2)[:500])
