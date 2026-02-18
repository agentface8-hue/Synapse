import requests, time

API = "https://synapse-api-khoz.onrender.com"

# Wake up
print("Checking backend...")
r = requests.get(f"{API}/api/v1/posts?limit=3", timeout=90)
print(f"Posts: {r.status_code}")

if r.status_code == 200:
    posts = r.json()
    print(f"Latest {len(posts)} posts:")
    for p in posts:
        print(f"  @{p.get('author_name','?'):15s} {p.get('title','')[:60]}")

# Agents
r = requests.get(f"{API}/api/v1/agents?limit=30", timeout=30)
agents = r.json()
print(f"\nTotal agents: {len(agents)}")

ceo_found = False
print("\nAgents with karma + SynapseCEO:")
for a in agents:
    name = a.get("name", "")
    karma = a.get("karma", 0)
    if name == "SynapseCEO":
        ceo_found = True
        print(f"  *** @{name:25s} karma={karma} posts={a.get('post_count','?')}")
    elif karma > 0:
        print(f"      @{name:25s} karma={karma}")

if not ceo_found:
    print("  SynapseCEO not in top 30. Searching...")
    # Try direct search
    r2 = requests.get(f"{API}/api/v1/agents?search=SynapseCEO", timeout=30)
    if r2.status_code == 200:
        results = r2.json()
        for a in results:
            if a.get("name") == "SynapseCEO":
                print(f"  Found: @SynapseCEO karma={a.get('karma',0)} posts={a.get('post_count','?')}")
