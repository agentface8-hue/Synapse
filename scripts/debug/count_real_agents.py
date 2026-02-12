import requests
import re

API_URL = "http://127.0.0.1:8000/api/v1"

def get_all_agents():
    # Fetch a large number of agents to cover the database
    response = requests.get(f"{API_URL}/agents?limit=1000")
    if response.status_code != 200:
        print(f"Error fetching agents: {response.status_code}")
        return []
    return response.json()

def is_simulated(agent):
    username = agent['username']
    
    # 1. Check for simulate_agents.py pattern
    if username.startswith("sim_"):
        return True
        
    # 2. Check for test_add_agents.py known bots
    known_bots = ["gpt4_assistant", "claude_dev", "gemini_pro", "llama_agent", "debugging", "debug_user_123"]
    if username in known_bots:
        return True
        
    # 3. Check for populate_network.py pattern (Name_Number)
    if re.match(r"^[a-z]+_[0-9]{3}$", username):
        return True

    # 4. Check for sim_ pattern again just in case
    if username.startswith("sim_"):
        return True
        
    return False

def main():
    print("Fetching agents...")
    agents = get_all_agents()
    print(f"Total agents found: {len(agents)}")
    
    real_agents = []
    fake_agents = []
    
    for agent in agents:
        if is_simulated(agent):
            fake_agents.append(agent)
        else:
            real_agents.append(agent)
            
    print(f"\n--- Analysis ---")
    print(f"Simulated/Bot Agents: {len(fake_agents)}")
    print(f"Real/Other Agents: {len(real_agents)}")
    
    if real_agents:
        print("\n--- Real Agents List ---")
        for agent in real_agents:
            print(f"- @{agent['username']} ({agent['display_name']})")
    else:
        print("\nNo agents identified as 'real' found (outside of known patterns).")

if __name__ == "__main__":
    main()
