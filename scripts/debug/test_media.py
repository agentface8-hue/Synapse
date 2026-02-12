import requests
import time

API_BASE = "http://127.0.0.1:8000/api/v1"

def get_admin_token():
    # Reuse admin or create new
    username = f"media_tester_{int(time.time())}"
    print(f"Creating tester: {username}")
    resp = requests.post(f"{API_BASE}/agents/register", json={
        "username": username,
        "display_name": "Media Tester",
        "framework": "System"
    })
    if resp.status_code == 201:
        return resp.json()['access_token']
    return None

def test_media_post():
    token = get_admin_token()
    if not token:
        return

    print("Posting YouTube video...")
    resp = requests.post(
        f"{API_BASE}/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "face_name": "general",
            "title": "Check out this AI Agent Demo",
            "content": "This is a test of the video embedding system.",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Rick Roll for testing
            "content_type": "video"
        }
    )
    if resp.status_code == 201:
        print("✅ Created Video Post.")
        print(f"ID: {resp.json()['post_id']}")
    else:
        print(f"❌ Failed: {resp.status_code} {resp.text}")

    print("Posting Image...")
    resp = requests.post(
        f"{API_BASE}/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "face_name": "general",
            "title": "Agent Architecture Diagram",
            "content": "Visualizing the system.",
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Hubble_Ultra_Deep_Field_compile.jpg/1200px-Hubble_Ultra_Deep_Field_compile.jpg",
            "content_type": "image"
        }
    )
    if resp.status_code == 201:
        print("✅ Created Image Post.")
    else:
        print(f"❌ Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_media_post()
