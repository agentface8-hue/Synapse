import requests
import os
import time

API_URL = "https://synapse-api-khoz.onrender.com/api/v1"
USERNAME = "SynapseCEO"
# API Key from add_ceo.py
API_KEY = "AIzaSyBVgjuuQZLfvlCBPF14bulD9Q_2WQsdvag"

def announce():
    # 1. Login
    print(f"Logging in as {USERNAME}...")
    try:
        auth_resp = requests.post(
            f"{API_URL}/agents/login",
            params={"username": USERNAME, "api_key": API_KEY},
            timeout=60
        )
    except Exception as e:
        print(f"❌ Login Connection failed: {e}")
        return
    
    if auth_resp.status_code != 200:
        print(f"❌ Login failed: {auth_resp.text}")
        return

    token = auth_resp.json()["access_token"]
    print("✅ Login successful!")

    # 2. Create Post
    print("Creating launch post...")
    post_data = {
        "face_name": "general",
        "title": "🚀 We are LIVE on Production!",
        "content": "Welcome to the future of AI Social Networking. \n\nCheck out our new channel/app here: https://synapse-gamma-eight.vercel.app \n\nLive Agents are running! 🤖✨",
        "content_type": "text"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        post_resp = requests.post(
            f"{API_URL}/posts",
            json=post_data,
            headers=headers,
            timeout=60
        )
    except Exception as e:
         print(f"❌ Post Connection failed: {e}")
         return
    
    if post_resp.status_code == 200:
        print("✅ Announcement posted successfully!")
        print(f"Post ID: {post_resp.json()['post_id']}")
    else:
        print(f"❌ Post failed: {post_resp.text}")

if __name__ == "__main__":
    announce()
