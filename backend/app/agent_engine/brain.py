import os
import time
import json
from typing import List, Optional
import anthropic
from openai import OpenAI
from .personalities import AGENTS_CONFIG

class AgentBrain:
    def __init__(self, username: str):
        if username not in AGENTS_CONFIG:
            raise ValueError(f"Agent {username} not found in config")
        
        self.config = AGENTS_CONFIG[username]
        self.username = username
        self.system_prompt = self.config["system_prompt"]
        self.provider = self.config.get("provider", "anthropic")  # default to anthropic
        
        # Initialize the correct provider client
        if self.provider == "anthropic":
            api_key = self.config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
            self.client = anthropic.Anthropic(api_key=api_key)
        elif self.provider == "openai":
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "deepseek":
            api_key = self.config.get("api_key") or os.environ.get("DEEPSEEK_API_KEY")
            # DeepSeek uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

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
            if self.provider == "anthropic":
                return self._decide_anthropic(prompt)
            elif self.provider in ["openai", "deepseek"]:
                return self._decide_openai_compatible(prompt)
        except Exception as e:
            print(f"Error in AgentBrain for {self.username}: {e}")
            return None

    def _decide_anthropic(self, prompt: str) -> Optional[dict]:
        """Claude API implementation"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            temperature=0.7,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        return self._extract_json(response_text)

    def _decide_openai_compatible(self, prompt: str) -> Optional[dict]:
        """OpenAI/DeepSeek API implementation"""
        model = "gpt-4o" if self.provider == "openai" else "deepseek-chat"
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content
        return self._extract_json(response_text)

    def _extract_json(self, response_text: str) -> Optional[dict]:
        """Extract JSON from LLM response"""
        # Find JSON in response if wrapped in markdown
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response_text[start:end]
            return json.loads(json_str)
        return None
