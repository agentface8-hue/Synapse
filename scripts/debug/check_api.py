import httpx
import json

try:
    print("Fetching /api/v1/agents...")
    resp = httpx.get("http://127.0.0.1:8000/api/v1/agents", timeout=10.0)
    print(f"Status: {resp.status_code}")
    print("Body:")
    try:
        print(json.dumps(resp.json(), indent=2))
    except:
        print(resp.text)
except Exception as e:
    print(f"Error: {e}")
