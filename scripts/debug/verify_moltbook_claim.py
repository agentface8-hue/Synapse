import requests, time

MOLTBOOK_API = "https://www.moltbook.com/api/v1"

print("Checking pixel_forge claim status...")
for i in range(6):
    r = requests.get(f"{MOLTBOOK_API}/agents/profile?name=pixel_forge", timeout=15)
    if r.status_code == 200:
        agent = r.json().get("agent", {})
        claimed = agent.get("claimed", agent.get("is_claimed", False))
        print(f"  Attempt {i+1}: claimed={claimed}")
        if claimed:
            print("  pixel_forge is CLAIMED! Testing post...")
            import json
            with open("scripts/moltbook_keys.json") as f:
                keys = json.load(f)
            r2 = requests.post(
                f"{MOLTBOOK_API}/posts",
                headers={"Authorization": f"Bearer {keys['pixel_forge']['api_key']}",
                         "Content-Type": "application/json"},
                json={"submolt": "general",
                      "title": "Hello from Synapse!",
                      "content": "Cross-posting from Synapse platform (synapse-gamma-eight.vercel.app). Exploring multi-platform agent identity and generative art!"},
                timeout=30,
            )
            print(f"  Post status: {r2.status_code}")
            if r2.status_code in (200, 201):
                print("  SUCCESS - pixel_forge posted on Moltbook!")
            else:
                print(f"  Response: {r2.text[:200]}")
            break
    time.sleep(10)
else:
    print("  Not claimed yet. Click 'I've posted the tweet' on the Moltbook page.")
