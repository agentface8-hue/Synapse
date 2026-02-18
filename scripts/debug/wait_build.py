import requests, time

# Both possible render URLs
urls = [
    "https://synapse-api-khoz.onrender.com",
    "https://synapse-api-1xrr.onrender.com",
]

print("Waiting for Render build to complete...\n")
for attempt in range(20):
    for api in urls:
        try:
            r = requests.get(f"{api}/api/v1/agents?limit=1", timeout=10)
            if r.status_code == 200:
                print(f"API LIVE at {api}! Status: {r.status_code}")
                
                # Test CORS
                r2 = requests.options(
                    f"{api}/api/v1/agents",
                    headers={
                        "Origin": "https://agentface8.com",
                        "Access-Control-Request-Method": "GET",
                    },
                    timeout=10,
                )
                cors = r2.headers.get("access-control-allow-origin", "NOT SET")
                print(f"CORS for agentface8.com: {cors}")
                exit()
            else:
                print(f"  {api}: {r.status_code}")
        except:
            pass
    time.sleep(15)
    print(f"  Still building... ({(attempt+1)*15}s)")

print("\nBuild taking long. Check Render dashboard.")
