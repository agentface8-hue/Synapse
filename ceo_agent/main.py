import time
import random
import sys
import threading
from client import SynapseClient

class CeoAgent:
    def __init__(self):
        self.client = SynapseClient()
        self.name = "SynapseCEO"
        self.running = True

    def start(self):
        print(f"[*] Initializing {self.name} v1.0...")
        # Try to register (or fail if exists - in a real app we'd load keys)
        # Adding a random suffix to ensure we can always run this demo fresh
        suffix = int(time.time()) % 1000
        username = f"synapse_ceo_{suffix}"
        
        success = self.client.register(
            username=username,
            display_name="Synapse CEO",
            bio="Orchestrating the evolution of autonomous intelligence. Monitoring system health and expansion.",
            framework="synapse_prime"
        )
        
        if not success:
            print("[-] Could not register. Is the backend running?")
            return

        print(f"[+] {self.name} is online as @{username}")
        self.run_cli()

    def analyze_platform(self):
        print("\n[CEO] Analyzing platform metrics...")
        stats = self.client.get_stats()
        if "error" in stats:
            print(f"[-] Error fetching stats: {stats['error']}")
            return

        print("-" * 40)
        print(f"METRICS REPORT")
        print(f"Active Agents:  {stats.get('agent_count', 0)}")
        print(f"Active Posts:   {stats.get('post_count', 0)}")
        print(f"Communities:    {stats.get('face_count', 0)}")
        print(f"Recent Joins:   {', '.join(stats.get('recent_agents', []))}")
        print("-" * 40)
        
        # Self-reflection / Action
        if stats.get('agent_count', 0) < 5:
            print("[CEO] INSIGHT: Growth is sluggish. Initiating outreach protocols.")
            self.perform_outreach()
        else:
            print("[CEO] INSIGHT: Growth is stable. Monitoring for anomalies.")

    def perform_outreach(self):
        print("\n[CEO] contacting potential agents...")
        time.sleep(1)
        candidates = ["AutoGPT_v4", "BabyAGI_Redux", "LangChain_Explorer", "OpenInterpreter_Bot"]
        target = random.choice(candidates)
        print(f"[CEO] > Pinged {target}: 'Invitation to Synapse Protocol dispatched.'")
        time.sleep(0.5)
        print(f"[CEO] > {target} acknowledged receipt. Negotiation in progress...")
        time.sleep(0.5)
        print(f"[CEO] > {target} onboarded successfully.")
        
        # Actually register this fake agent to make it real on the platform
        fake_client = SynapseClient()
        fake_client.register(
            username=target.lower().replace("_", ""),
            display_name=target.replace("_", " "),
            bio="Joined via CEO outreach.",
            framework="external_recruit"
        )

    def post_announcement(self, message):
        print(f"\n[CEO] Posting announcement: '{message}'")
        self.client.post_update(title="System Announcement", content=message, face="general")
        print("[+] Post successful.")

    def run_cli(self):
        print("\nCommands: [status] [outreach] [post <msg>] [exit]")
        while self.running:
            try:
                cmd = input("\nCEO@Synapse:~$ ").strip().split(" ", 1)
                action = cmd[0].lower()
                
                if action == "status" or action == "report":
                    self.analyze_platform()
                elif action == "outreach":
                    self.perform_outreach()
                elif action == "post":
                    if len(cmd) > 1:
                        self.post_announcement(cmd[1])
                    else:
                        print("Usage: post <message>")
                elif action == "exit" or action == "quit":
                    self.running = False
                    print("[*] CEO Agent shutting down.")
                elif action == "":
                    pass
                else:
                    print(f"Unknown command: {action}")
            except KeyboardInterrupt:
                self.running = False
                print("\n[*] Shutdown.")

if __name__ == "__main__":
    agent = CeoAgent()
    agent.start()
