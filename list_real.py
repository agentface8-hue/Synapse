import requests
import re
import json

API_URL = "http://127.0.0.1:8000/api/v1"

def main():
    try:
        response = requests.get(f"{API_URL}/agents?limit=1000")
        agents = response.json()
    except:
        print("Failed to fetch.")
        return

    real = []
    
    # EXACT known bots filter
    known_bots = ["gpt4_assistant", "claude_dev", "gemini_pro", "llama_agent", "debugging", "debug_user_123"]

    for a in agents:
        u = a['username']
        # Filter logic
        if u.startswith("sim_"): continue
        if u in known_bots: continue
        if re.match(r"^[a-z]+_[0-9]{3}$", u): continue # name_123
        
        real.append(u)

    with open("final_list.txt", "w") as f:
        for name in real:
            f.write(name + "\n")

if __name__ == "__main__":
    main()
