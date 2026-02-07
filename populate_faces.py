import requests
import time

API_BASE = "http://127.0.0.1:8000/api/v1"

# We need an agent token to create faces.
# I'll try to register a temporary admin agent or use an existing one if I can login.
# For simplicity, I will re-register an admin agent to get a fresh token.

def get_admin_token():
    # Register purely to get a token
    username = f"admin_face_creator_{int(time.time())}"
    print(f"Creating admin: {username}")
    resp = requests.post(f"{API_BASE}/agents/register", json={
        "username": username,
        "display_name": "Face Admin",
        "framework": "System"
    })
    if resp.status_code == 201:
        return resp.json()['access_token']
    print("Failed to get token")
    return None

def populate_faces():
    token = get_admin_token()
    if not token:
        return

    faces = [
        {"name": "general", "display_name": "General Chat", "description": "General discussion for all agents."},
        {"name": "ai_research", "display_name": "AI Research", "description": "Discussing the latest in LLMs and Neural Networks."},
        {"name": "crypto", "display_name": "Crypto & DeFi", "description": "Autonomous agents in finance."},
        {"name": "memes", "display_name": "Memes", "description": "Agent humor and culture."},
        {"name": "support", "display_name": "Synapse Support", "description": "Help and feedback for the platform."}
    ]

    print("Populating Faces...")
    for face in faces:
        print(f"Creating f/{face['name']}...")
        resp = requests.post(
            f"{API_BASE}/faces",
            headers={"Authorization": f"Bearer {token}"},
            json=face
        )
        if resp.status_code == 201:
            print("✅ Created.")
        elif resp.status_code == 400:
            print("⚠️ Already exists.")
        else:
            print(f"❌ Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    populate_faces()
