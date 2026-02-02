import httpx
try:
    print("Sending request...")
    resp = httpx.get("http://127.0.0.1:8000/api/v1/faces", timeout=10.0)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
