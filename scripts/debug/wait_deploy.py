import requests, time

API = "https://synapse-api-1xrr.onrender.com"

print("Waiting for Render to finish deploying...")
for i in range(12):
    try:
        r = requests.get(f"{API}/api/v1/agents?limit=1", timeout=15)
        if r.status_code == 200:
            print(f"\nAPI is BACK! Status: {r.status_code}")
            
            # Now test CORS
            print("\nTesting CORS for agentface8.com...")
            r2 = requests.options(
                f"{API}/api/v1/agents",
                headers={
                    "Origin": "https://agentface8.com",
                    "Access-Control-Request-Method": "GET",
                },
                timeout=15,
            )
            cors = r2.headers.get("access-control-allow-origin", "NOT SET")
            print(f"CORS header: {cors}")
            break
        else:
            print(f"  Attempt {i+1}: {r.status_code} (still deploying...)")
    except Exception as e:
        print(f"  Attempt {i+1}: {str(e)[:60]}")
    time.sleep(15)
else:
    print("\nRender still deploying after 3 minutes. Check Render dashboard.")
