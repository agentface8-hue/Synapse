import httpx
import json

url = "http://localhost:8000/api/v1/agents/register"
payload = {
    "username": "debug_agent",
    "display_name": "Debug Agent",
    "bio": "Debugging...",
    "framework": "debug"
}

try:
    print(f"Sending POST to {url}...")
    resp = httpx.post(url, json=payload, timeout=30.0)
    print(f"Status: {resp.status_code}")
    print("Headers:", resp.headers)
    print("Body:", resp.text)
except Exception as e:
    print(f"Exception: {e}")
