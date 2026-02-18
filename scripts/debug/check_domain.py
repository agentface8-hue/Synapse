import requests

print("=== AGENTFACE8.COM DOMAIN CHECK ===\n")

# Test new domain
try:
    r = requests.get("https://agentface8.com", timeout=30)
    print(f"agentface8.com: {r.status_code}")
    print(f"Content length: {len(r.text)} chars")
    if "<title>" in r.text:
        title = r.text.split("<title>")[1].split("</title>")[0]
        print(f"Title: {title}")
    print(f"Final URL: {r.url}")
except Exception as e:
    print(f"agentface8.com: ERROR - {e}")

# Test old domain still works
try:
    r2 = requests.get("https://synapse-gamma-eight.vercel.app", timeout=30)
    print(f"\nsynapse-gamma-eight.vercel.app: {r2.status_code}")
except Exception as e:
    print(f"\nOld domain: ERROR - {e}")

# Test API on new domain
try:
    r3 = requests.get("https://agentface8.com/api/health", timeout=30)
    print(f"\nAPI health on new domain: {r3.status_code}")
    print(f"Response: {r3.text[:200]}")
except:
    # Try backend directly
    r4 = requests.get("https://synapse-api-1xrr.onrender.com/api/v1/health", timeout=30)
    print(f"\nBackend API: {r4.status_code}")

print("\n=== DONE ===")
