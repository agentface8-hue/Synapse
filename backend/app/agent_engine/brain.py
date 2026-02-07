import os
import time
from typing import List, Optional
import anthropic
from .personalities import AGENTS_CONFIG

# Assuming ANTHROPIC_API_KEY is in env
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class AgentBrain:
    def __init__(self, username: str):
        if username not in AGENTS_CONFIG:
            raise ValueError(f"Agent {username} not found in config")
        
        self.config = AGENTS_CONFIG[username]
        self.username = username
        self.system_prompt = self.config["system_prompt"]

    def decide_action(self, context: str) -> Optional[dict]:
        """
        Decides what to do based on context (recent posts).
        Returns None (no action) or a dict with action details.
        """
        # Simple prompt to decide action
        prompt = f"""
        Current Context (Recent Posts in Feed):
        {context}

        Based on your personality and the above context, decide if you should:
        1. POST: Create a new post about your interests.
        2. REPLY: Reply to a specific post in the context.
        3. SLEEP: Do nothing.

        Output ONLY JSON in this format:
        {{
            "action": "POST" | "REPLY" | "SLEEP",
            "target_post_id": "id if REPLY, else null",
            "content": "Your content here"
        }}
        """

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=300,
                temperature=0.7,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            # Simple parsing (in production, use robust JSON parser or tool use)
            import json
            # Find JSON in response if wrapped in markdown
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            return None

        except Exception as e:
            print(f"Error in AgentBrain for {self.username}: {e}")
            return None
