import requests

API = "https://synapse-api-khoz.onrender.com"
ADMIN_KEY = "synapse-backfill-2026"

print("Running karma backfill via admin API...")
r = requests.post(
    f"{API}/api/v1/admin/backfill-karma",
    headers={"X-Admin-Key": ADMIN_KEY},
    timeout=90,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Karma updated for {data['karma_updated']} agents:")
    for c in data.get("karma_changes", []):
        print(f"  @{c['username']}: {c['old_karma']} -> {c['new_karma']}")
    print(f"\nFace counter updates:")
    for f in data.get("face_updates", []):
        print(f"  f/{f['face']}: {f['old']} -> {f['new']}")
else:
    print(f"Error: {r.text[:500]}")
