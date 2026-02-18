import requests

urls = [
    "https://synapse-api-aqhk.onrender.com/",
    "https://synapse-api-aqhk.onrender.com/api/v1/posts",
    "https://synapse-api-aqhk.onrender.com/api/v1/agents",
    "https://synapse-api-aqhk.onrender.com/api/v1/faces",
    "https://synapse-api-aqhk.onrender.com/posts",
    "https://synapse-api-aqhk.onrender.com/agents",
]

for url in urls:
    try:
        r = requests.get(url, timeout=60)
        text = r.text[:150].replace("\n"," ")
        print(f"{r.status_code} {url}")
        print(f"    {text}")
    except Exception as e:
        print(f"ERR {url}: {e}")
