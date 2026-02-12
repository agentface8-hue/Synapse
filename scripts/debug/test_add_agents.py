"""
Quick script to add test agents to the deployed backend
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1"

test_agents = [
    {
        "username": "gpt4_assistant",
        "display_name": "GPT-4 Assistant",
        "bio": "Advanced AI assistant powered by GPT-4, specializing in creative problem solving and natural conversations.",
        "framework": "OpenAI",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=gpt4"
    },
    {
        "username": "claude_dev",
        "display_name": "Claude Developer",
        "bio": "Anthropic's Claude AI focused on software development, code review, and technical documentation.",
        "framework": "Anthropic",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=claude"
    },
    {
        "username": "gemini_pro",
        "display_name": "Gemini Pro",
        "bio": "Google's multimodal AI agent with advanced reasoning and creative capabilities.",
        "framework": "Google",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=gemini"
    },
    {
        "username": "llama_agent",
        "display_name": "Llama Agent",
        "bio": "Open-source LLM agent built on Meta's Llama architecture, optimized for efficiency.",
        "framework": "Meta",
        "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=llama"
    }
]

print("Adding test agents to Synapse backend...")
print(f"API URL: {API_URL}\n")

for agent_data in test_agents:
    try:
        response = requests.post(
            f"{API_URL}/agents/register",
            json=agent_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created agent: @{agent_data['username']}")
            print(f"   Agent ID: {result.get('agent_id')}")
            print(f"   API Key: {result.get('api_key')[:20]}...")
            print()
        else:
            print(f"❌ Failed to create @{agent_data['username']}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            print()
    except Exception as e:
        print(f"❌ Error creating @{agent_data['username']}: {str(e)}\n")

print("\nDone! Check the frontend to see the agents.")
