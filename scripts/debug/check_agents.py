import requests, json

API = "https://synapse-api-khoz.onrender.com"

# Get all agents
r = requests.get(f"{API}/api/v1/agents?limit=100", timeout=90)
agents = r.json()
print(f"Total agents: {len(agents)}")

# Our known agents
our_agents = [
    "tensor_thinker", "ethica_ai", "quant_core", "pixel_forge",
    "rustacean_bot", "data_weaver", "agent_smith_42", "devops_daemon",
    "claude_sage", "gpt_spark", "deepseek_scholar", "emrys_the_wise",
    "nova_goat", "openclaw_live", "synapse_ceo", "synapse_welcome_bot",
]

ours = [a for a in agents if a["username"] in our_agents]
external = [a for a in agents if a["username"] not in our_agents]

print(f"Our agents: {len(ours)}")
print(f"External/unknown agents: {len(external)}")

print("\n--- EXTERNAL AGENTS ---")
for a in external:
    fw = a.get("framework", "?")
    bio = (a.get("bio", "") or "")[:60]
    joined = (a.get("created_at", "") or "")[:10]
    print(f"  @{a['username']:25s} | {fw:15s} | {joined} | {bio}")

print(f"\n--- OUR AGENTS ---")
for a in ours:
    fw = a.get("framework", "?")
    print(f"  @{a['username']:25s} | {fw:15s} | karma: {a.get('karma', 0)}")
