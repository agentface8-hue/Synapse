import requests, os
key = os.environ.get("GEMINI_API_KEY", "AIzaSyBIfu65sEOA1WzKA9PtxdofYxQzwnyQaHc")
r = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
    params={"key": key},
    json={"contents": [{"parts": [{"text": "Say hello in exactly 5 words"}]}]},
    timeout=15,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Response: {r.json()['candidates'][0]['content']['parts'][0]['text']}")
else:
    print(f"Error: {r.text[:300]}")
