import requests

url = "http://127.0.0.1:8000/api/v1/agents/register"
data = {
    "username": "debug_user_123",
    "display_name": "Debug User",
    "bio": "Debugging",
    "framework": "Debug"
}
print(f"POSTing to {url}")
response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
