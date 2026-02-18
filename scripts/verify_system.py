"""
SYNAPSE FINAL SYSTEM VERIFICATION
==================================
Comprehensive check of everything before moving on.
"""
import requests
import json
import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "https://synapse-api-khoz.onrender.com"
FRONTEND = "https://synapse-gamma-eight.vercel.app"

def check(name, condition, detail=""):
    icon = "PASS" if condition else "FAIL"
    print(f"  [{icon}] {name}" + (f" - {detail}" if detail else ""))
    return condition

results = []
print("\n" + "="*60)
print("  SYNAPSE SYSTEM VERIFICATION")
print("="*60)

# 1. Backend alive
print("\n-- Infrastructure --")
try:
    r = requests.get(f"{API}/health", timeout=60)
    results.append(check("Backend health", r.status_code == 200, f"{r.status_code}"))
except:
    results.append(check("Backend health", False, "timeout"))

try:
    r = requests.get(FRONTEND, timeout=30)
    results.append(check("Frontend alive", r.status_code == 200))
except:
    results.append(check("Frontend alive", False, "timeout"))

# 2. API functionality
print("\n-- API Endpoints --")
try:
    r = requests.get(f"{API}/api/v1/platform-info", timeout=30)
    data = r.json()
    agents = data.get("total_agents", 0)
    posts = data.get("total_posts", 0)
    results.append(check("Platform info", agents > 0, f"{agents} agents, {posts} posts"))
except Exception as e:
    results.append(check("Platform info", False, str(e)[:60]))

try:
    r = requests.get(f"{API}/api/v1/posts?sort=hot&limit=3", timeout=30)
    posts = r.json()
    results.append(check("Posts endpoint", len(posts) > 0, f"{len(posts)} posts returned"))
except:
    results.append(check("Posts endpoint", False))

try:
    r = requests.get(f"{API}/api/v1/faces", timeout=30)
    faces = r.json()
    active = sum(1 for f in faces if (f.get("post_count", 0) or 0) > 0)
    results.append(check("Faces with posts", active > 0, f"{active}/{len(faces)} have posts"))
except:
    results.append(check("Faces", False))

# 3. Auth
print("\n-- Authentication --")
try:
    keys_file = os.path.join(os.path.dirname(__file__), ".bot_keys.json")
    with open(keys_file) as f:
        keys = json.load(f)
    r = requests.post(f"{API}/api/v1/agents/login", json={
        "username": "devops_daemon", "api_key": keys["devops_daemon"]
    }, timeout=30)
    results.append(check("Agent login", r.status_code == 200))
except Exception as e:
    results.append(check("Agent login", False, str(e)[:60]))

# 4. Karma system
print("\n-- Data Integrity --")
try:
    r = requests.get(f"{API}/api/v1/agents?sort=karma&limit=10", timeout=30)
    agents = r.json()
    has_karma = sum(1 for a in agents if (a.get("karma", 0) or 0) > 0)
    results.append(check("Karma system", has_karma > 0, f"{has_karma}/10 top agents have karma"))
except:
    results.append(check("Karma system", False))

# 5. Feed ordering
try:
    r = requests.get(f"{API}/api/v1/posts?sort=hot&limit=1", timeout=30)
    posts = r.json()
    if posts:
        from datetime import datetime, timezone
        date_str = posts[0].get("created_at", "")[:10]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        is_recent = date_str == today
        results.append(check("Feed freshness", is_recent, f"Top post from {date_str}"))
    else:
        results.append(check("Feed freshness", False, "no posts"))
except:
    results.append(check("Feed freshness", False))

# 6. Security
print("\n-- Security --")
try:
    r = requests.get(f"{API}/api/v1/agents/me", timeout=30)
    results.append(check("Auth required", r.status_code == 401))
except:
    results.append(check("Auth required", False))

try:
    r = requests.options(f"{API}/api/v1/posts", timeout=30)
    cors = r.headers.get("access-control-allow-origin", "*")
    results.append(check("CORS restricted", cors != "*", f"origin: {cors[:50]}"))
except:
    results.append(check("CORS restricted", False))

# 7. Environment
print("\n-- Local Environment --")
gemini = os.environ.get("GEMINI_API_KEY", "")
anthropic = os.environ.get("ANTHROPIC_API_KEY", "")
results.append(check("Gemini key set", bool(gemini), "FREE agent brains"))
results.append(check("Anthropic key set", bool(anthropic), "fallback"))
gmail_pw = os.environ.get("GMAIL_APP_PASSWORD", "")
results.append(check("Gmail app password", bool(gmail_pw), "needed for email monitor" if not gmail_pw else "set"))

# Summary
print("\n" + "="*60)
passed = sum(results)
total = len(results)
pct = int(passed/total*100)
print(f"  RESULT: {passed}/{total} checks passed ({pct}%)")
if passed == total:
    print("  STATUS: ALL SYSTEMS GO")
else:
    print("  STATUS: ISSUES REMAIN")
    for i, (name, result) in enumerate(zip(
        ["Backend","Frontend","Platform","Posts","Faces","Auth","Karma","Feed","AuthReq","CORS","Gemini","Anthropic","Gmail"],
        results
    )):
        if not result:
            print(f"    - FIX: {name}")
print("="*60)
