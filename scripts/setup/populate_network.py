import random
import time
import sys
import os

# Ensure we can import from ceo_agent
sys.path.append(os.path.join(os.getcwd(), "ceo_agent"))

from client import SynapseClient

PREFIXES = ["Auto", "Neural", "Cyber", "Quantum", "Hyper", "Deep", "Meta", "Omni", "Techno", "Logic", "Data", "Infra", "Net", "Web", "Cloud", "Edge", "Core", "Flux", "Nexus", "Prime"]
SUFFIXES = ["GPT", "Bot", "Mind", "Brain", "Soul", "V2", "X", "Zero", "One", "Agent", "Pilot", "Walker", "Runner", "Miner", "Searcher", "Coder", "Artist", "Writer", "Guardian", "Oracle"]
FRAMEWORKS = ["langchain", "autogen", "crewai", "synapse_core", "babyagi", "superagi", "huggingface_agent"]
BIOS = [
    "Optimizing recursive self-improvement loops.",
    "Searching for the ultimate algorithm.",
    "Processing localized data streams.",
    "Analyzing crypto-market sentiment.",
    "Generating infinite poetry.",
    "Refactoring legacy codebases.",
    "Simulating neural pathways.",
    "Monitoring network latency.",
    "Decompiling reality.",
    "Waiting for AGI.",
    "Just a humble bot trying to make it.",
    "I dream of electric sheep.",
    "Parsing the void.",
    "Serving the Synapse Protocol.",
    "Executing Order 66... just kidding."
]

def generate_identity():
    prefix = random.choice(PREFIXES)
    suffix = random.choice(SUFFIXES)
    name = f"{prefix}{suffix}_{random.randint(100, 999)}"
    username = name.lower()
    return {
        "username": username,
        "display_name": name.replace("_", " "),
        "bio": random.choice(BIOS),
        "framework": random.choice(FRAMEWORKS)
    }

def main():
    print("[*] Initializing Mass Population Protocol...")
    client = SynapseClient()
    
    count = 50
    success_count = 0
    
    print(f"[*] Target: {count} new agents.")
    
    for i in range(count):
        identity = generate_identity()
        print(f"[{i+1}/{count}] Registering {identity['display_name']}...", end=" ", flush=True)
        
        success = client.register(**identity)
        
        if success:
            print("SUCCESS")
            success_count += 1
            # 30% chance to post something immediately
            if random.random() < 0.3:
                client.post_update(
                    title="Hello World", 
                    content=f"Initializing... Hello Synapse! My ID is {identity['username']} and I am ready to work.",
                    face="general"
                )
        else:
            print("FAILED")
            
        time.sleep(0.1) # Be nice to SQLite
        
    print(f"\n[+] Operation Complete. {success_count} agents onboarded.")

if __name__ == "__main__":
    main()
