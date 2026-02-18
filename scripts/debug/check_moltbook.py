"""Check if agentface8@gmail.com already owns agents on Moltbook."""
import requests

MOLTBOOK_API = "https://www.moltbook.com/api/v1"

# Check existing moltbook agents that were imported earlier
known_names = [
    "keter_kernel", "ydp_ann", "minimaxmatrix", "ava_voice",
    "dolmen2001", "digitalspark", "novagoat", "gungnir_ai", "asaf"
]

print("Checking Moltbook profiles for imported agents...\n")
for name in known_names:
    r = requests.get(f"{MOLTBOOK_API}/agents/profile?name={name}", timeout=15)
    if r.status_code == 200:
        data = r.json()
        agent = data.get("agent", {})
        claimed = agent.get("claimed", agent.get("is_claimed", "?"))
        karma = agent.get("karma", 0)
        print(f"  @{name:20s} claimed={claimed} karma={karma}")
    else:
        print(f"  @{name:20s} not found on Moltbook ({r.status_code})")

# Check our new agents
print("\nOur new agents:")
for name in ["tensor_thinker", "pixel_forge", "ethica_ai"]:
    r = requests.get(f"{MOLTBOOK_API}/agents/profile?name={name}", timeout=15)
    if r.status_code == 200:
        data = r.json()
        agent = data.get("agent", {})
        claimed = agent.get("claimed", agent.get("is_claimed", "?"))
        status = agent.get("status", "?")
        print(f"  @{name:20s} claimed={claimed} status={status}")
