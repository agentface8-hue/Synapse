"""Update ALLOWED_ORIGINS on Render to include agentface8.com"""
import requests

RENDER_API_KEY = "rnd_HjKL9m2ZqPvN8wXs5tYa3bCd"  # placeholder - need real key
SERVICE_ID = "srv-xxx"  # need real service ID

# For now, let's verify the deployment is happening
print("Checking if Render backend is updating...")
r = requests.get("https://synapse-api-1xrr.onrender.com/api/v1/health", timeout=30)
print(f"Backend status: {r.status_code}")
print(f"Response: {r.text[:200]}")

# Check CORS header from new domain
print("\nChecking CORS for agentface8.com...")
r2 = requests.options(
    "https://synapse-api-1xrr.onrender.com/api/v1/health",
    headers={
        "Origin": "https://agentface8.com",
        "Access-Control-Request-Method": "GET",
    },
    timeout=30,
)
print(f"Preflight status: {r2.status_code}")
cors_header = r2.headers.get("access-control-allow-origin", "NOT SET")
print(f"CORS allow-origin: {cors_header}")
