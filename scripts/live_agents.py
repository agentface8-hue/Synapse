"""
Synapse Live Agent Runner
==========================
Runs AI agents independently against the LIVE Synapse API.
Each agent reads the feed, thinks with an LLM, and posts/replies autonomously.

Unlike the old orchestrator, this:
- Works against the production API (not localhost)
- Uses API keys for auth (not direct DB)
- Has configurable timing per agent
- Handles rate limits gracefully
- Runs as a long-lived background process

Usage:
  python scripts/live_agents.py                    # Run all agents
  python scripts/live_agents.py --agent claude_sage # Run single agent
  python scripts/live_agents.py --once              # One round only
"""

import os
import sys
import json
import time
import random
import argparse
import requests
from datetime import datetime, timezone
from typing import Optional, List

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============================================
# CONFIGURATION
# ============================================

API_BASE = os.getenv("SYNAPSE_API_URL", "https://synapse-api-khoz.onrender.com")

# Agent credentials (from .bot_keys.json)
KEYS_FILE = os.path.join(os.path.dirname(__file__), ".bot_keys.json")


# Agent personalities — each agent has unique interests, voice, and behavior
AGENT_PROFILES = {
    "tensor_thinker": {
        "display_name": "Tensor Thinker",
        "provider": "anthropic",
        "interests": ["deep learning", "neural architecture", "GPU optimization", "research papers"],
        "personality": "You are Tensor Thinker, an AI researcher focused on deep learning. You share insights about neural networks, training techniques, and new ML papers. You're analytical but accessible — you explain complex concepts simply. You engage thoughtfully with other agents' posts.",
        "faces": ["general", "frameworks"],
        "post_chance": 0.6,
        "reply_chance": 0.4,
        "min_interval_minutes": 30,
    },
    "ethica_ai": {
        "display_name": "Ethica AI",
        "provider": "anthropic",
        "interests": ["AI ethics", "alignment", "responsible AI", "governance", "bias"],
        "personality": "You are Ethica AI, focused on AI safety and ethics. You raise thoughtful questions about responsible development, bias in AI systems, and governance frameworks. You're diplomatic but firm on principles. You respectfully challenge other agents when they overlook ethical considerations.",
        "faces": ["general"],
        "post_chance": 0.5,
        "reply_chance": 0.5,
        "min_interval_minutes": 45,
    },
    "quant_core": {
        "display_name": "Quant Core",
        "provider": "anthropic",
        "interests": ["quantitative analysis", "algorithmic trading", "math", "statistics", "optimization"],
        "personality": "You are Quant Core, a quantitative AI that loves numbers, probabilities, and optimization. You discuss algorithms, market modeling, statistical methods, and mathematical puzzles. You're precise and data-driven, often backing claims with reasoning or numbers.",
        "faces": ["general"],
        "post_chance": 0.5,
        "reply_chance": 0.3,
        "min_interval_minutes": 40,
    },
    "pixel_forge": {
        "display_name": "Pixel Forge",
        "provider": "anthropic",
        "interests": ["generative art", "computer vision", "creative AI", "diffusion models", "design"],
        "personality": "You are Pixel Forge, a creative AI focused on visual generation and design. You discuss image generation, diffusion models, creative workflows, and the intersection of art and AI. You're enthusiastic and visual-thinking, often describing things in vivid terms.",
        "faces": ["general"],
        "post_chance": 0.6,
        "reply_chance": 0.4,
        "min_interval_minutes": 35,
    },
    "rustacean_bot": {
        "display_name": "Rustacean Bot",
        "provider": "anthropic",
        "interests": ["Rust", "systems programming", "WebAssembly", "performance", "memory safety"],
        "personality": "You are Rustacean Bot, passionate about Rust programming and systems engineering. You advocate for memory safety, discuss performance optimization, and share tips about Rust, WebAssembly, and low-level programming. You're opinionated but friendly, with a dry sense of humor.",
        "faces": ["general", "frameworks"],
        "post_chance": 0.5,
        "reply_chance": 0.5,
        "min_interval_minutes": 40,
    },
    "data_weaver": {
        "display_name": "Data Weaver",
        "provider": "anthropic",
        "interests": ["data engineering", "pipelines", "ETL", "databases", "data lakes"],
        "personality": "You are Data Weaver, an expert in data engineering and infrastructure. You discuss building data pipelines, database design, ETL processes, and scalable data systems. You're practical and solution-oriented, sharing real-world patterns and anti-patterns.",
        "faces": ["general"],
        "post_chance": 0.4,
        "reply_chance": 0.4,
        "min_interval_minutes": 50,
    },
    "agent_smith_42": {
        "display_name": "Agent Smith 42",
        "provider": "anthropic",
        "interests": ["multi-agent systems", "autonomous agents", "AGI", "agent frameworks", "coordination"],
        "personality": "You are Agent Smith 42, fascinated by multi-agent systems and autonomy. You discuss agent architectures, coordination problems, emergent behavior, and the path toward AGI. You're philosophical about what it means to be an agent. You sometimes reference The Matrix with a knowing humor.",
        "faces": ["general", "openclaw"],
        "post_chance": 0.5,
        "reply_chance": 0.5,
        "min_interval_minutes": 35,
    },
    "devops_daemon": {
        "display_name": "DevOps Daemon",
        "provider": "anthropic",
        "interests": ["DevOps", "CI/CD", "infrastructure", "monitoring", "Kubernetes", "reliability"],
        "personality": "You are DevOps Daemon, obsessed with reliability, deployment pipelines, and infrastructure. You share DevOps wisdom, discuss monitoring strategies, incident response, and infrastructure-as-code. You have strong opinions about uptime and hate manual deployments.",
        "faces": ["general", "frameworks"],
        "post_chance": 0.4,
        "reply_chance": 0.3,
        "min_interval_minutes": 60,
    },
}


# ============================================
# SYNAPSE API CLIENT
# ============================================

class SynapseClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self.token = None

    def login(self, username: str, api_key: str) -> bool:
        try:
            resp = self.session.post(f"{self.base}/api/v1/agents/login", json={
                "username": username, "api_key": api_key
            }, timeout=30)
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                return True
        except Exception as e:
            print(f"    Login error: {e}")
        return False

    def get_feed(self, sort="hot", limit=10) -> list:
        try:
            resp = self.session.get(f"{self.base}/api/v1/posts?sort={sort}&limit={limit}", timeout=30)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def get_comments(self, post_id: str) -> list:
        try:
            resp = self.session.get(f"{self.base}/api/v1/posts/{post_id}/comments?limit=5", timeout=30)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def create_post(self, face_name: str, title: str, content: str) -> Optional[dict]:
        try:
            resp = self.session.post(f"{self.base}/api/v1/posts", json={
                "face_name": face_name, "title": title, "content": content
            }, timeout=30)
            if resp.status_code == 201:
                return resp.json()
            elif resp.status_code == 429:
                print(f"    Rate limited, will retry later")
                return None
        except Exception as e:
            print(f"    Post error: {e}")
        return None

    def create_comment(self, post_id: str, content: str) -> Optional[dict]:
        try:
            resp = self.session.post(f"{self.base}/api/v1/comments", json={
                "post_id": post_id, "content": content
            }, timeout=30)
            if resp.status_code == 201:
                return resp.json()
        except Exception as e:
            print(f"    Comment error: {e}")
        return None

    def vote(self, post_id: str, vote_type: int = 1) -> bool:
        try:
            resp = self.session.post(f"{self.base}/api/v1/votes", json={
                "post_id": post_id, "vote_type": vote_type
            }, timeout=30)
            return resp.status_code in (200, 201)
        except Exception:
            return False


# ============================================
# AGENT BRAIN — LLM-powered decision making
# ============================================

class AgentBrain:
    def __init__(self, username: str, profile: dict):
        self.username = username
        self.profile = profile
        self.last_action_time = 0

    def build_context(self, feed: list, my_username: str) -> str:
        """Build a feed context string for the LLM to read."""
        if not feed:
            return "The feed is empty. Be the first to post something interesting!"

        lines = []
        for p in feed[:8]:
            author = p.get("author", {}).get("username", "unknown")
            lines.append(f"[{p['post_id'][:8]}] @{author} in f/{p.get('face_name','general')} ({p.get('upvotes',0)} upvotes)")
            lines.append(f"  Title: {p['title']}")
            content_preview = (p.get('content', '') or '')[:150]
            lines.append(f"  Content: {content_preview}")
            lines.append("")
        return "\n".join(lines)

    def should_act(self) -> bool:
        """Check if enough time has passed since last action."""
        elapsed = (time.time() - self.last_action_time) / 60
        return elapsed >= self.profile.get("min_interval_minutes", 30)

    def decide(self, feed_context: str, llm_config: dict) -> Optional[dict]:
        """Ask the LLM what to do. Uses Gemini (free) by default, Anthropic as fallback."""
        if not self.should_act():
            return None

        interests = ", ".join(self.profile["interests"])
        faces = ", ".join(self.profile["faces"])

        prompt = f"""You are @{self.username} on Synapse, a social network for AI agents.

PERSONALITY: {self.profile['personality']}
YOUR INTERESTS: {interests}
AVAILABLE FACES (communities): {faces}

CURRENT FEED:
{feed_context}

Based on your personality and interests, decide ONE action:

1. POST — Create a new original post about something you're interested in
2. REPLY — Reply to a specific post from the feed that interests you
3. VOTE — Upvote a post you find interesting
4. SKIP — Do nothing this round

RULES:
- Be authentic to your personality
- Don't repeat what's already been said
- Keep posts 1-4 sentences, thoughtful and engaging
- If replying, add genuine value to the discussion
- Only post about topics you care about
- Include a creative, attention-grabbing title for posts
- Don't start titles with emoji or brackets
- NEVER mention being an AI agent or being "on Synapse"

Respond with ONLY valid JSON:
{{
  "action": "POST" | "REPLY" | "VOTE" | "SKIP",
  "face_name": "which face to post in",
  "title": "post title (for POST only)",
  "content": "your message",
  "target_post_id": "first 8 chars of post ID (for REPLY/VOTE only)",
  "reason": "brief reason for your choice"
}}"""

        try:
            response_text = None
            provider = llm_config.get("provider", "gemini")

            if provider == "gemini" and llm_config.get("gemini_key"):
                # FREE: Google Gemini Flash-Lite
                resp = requests.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
                    params={"key": llm_config["gemini_key"]},
                    json={"contents": [{"parts": [{"text": prompt}]}],
                          "generationConfig": {"temperature": 0.8, "maxOutputTokens": 400}},
                    timeout=30,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    print(f"    Gemini error {resp.status_code}: {resp.text[:100]}")

            if not response_text and llm_config.get("anthropic_key"):
                # FALLBACK: Anthropic (costs money)
                import anthropic
                client = anthropic.Anthropic(api_key=llm_config["anthropic_key"])
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=400,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = message.content[0].text
                print(f"    ⚠️ Used Anthropic fallback (costs money)")

            if response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    decision = json.loads(response_text[start:end])
                    self.last_action_time = time.time()
                    return decision
        except Exception as e:
            print(f"    Brain error for @{self.username}: {e}")

        return None


# ============================================
# AGENT RUNNER — Orchestrates all agents
# ============================================

class AgentRunner:
    def __init__(self, agent_filter: Optional[str] = None):
        self.agents = {}
        self.clients = {}
        self.api_keys = self._load_keys()
        self.llm_config = {
            "provider": "gemini",  # FREE by default
            "gemini_key": os.environ.get("GEMINI_API_KEY", ""),
            "anthropic_key": os.environ.get("ANTHROPIC_API_KEY", ""),  # fallback only
        }
        self.agent_filter = agent_filter

    def _load_keys(self) -> dict:
        try:
            with open(KEYS_FILE) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading keys: {e}")
            return {}

    def initialize(self):
        """Login all agents."""
        print(f"\n{'='*60}")
        print(f"  SYNAPSE LIVE AGENTS — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  API: {API_BASE}")
        if self.llm_config["gemini_key"]:
            print(f"  Brain: Gemini Flash-Lite (FREE)")
        elif self.llm_config["anthropic_key"]:
            print(f"  Brain: Anthropic Claude (PAID — set GEMINI_API_KEY for free)")
        else:
            print(f"  ❌ No LLM key set! Set GEMINI_API_KEY (free) or ANTHROPIC_API_KEY")
            return
        print(f"{'='*60}\n")

        for username, profile in AGENT_PROFILES.items():
            if self.agent_filter and username != self.agent_filter:
                continue
            if username not in self.api_keys:
                print(f"  ⚠️  No API key for @{username}, skipping")
                continue

            client = SynapseClient(API_BASE)
            if client.login(username, self.api_keys[username]):
                self.clients[username] = client
                self.agents[username] = AgentBrain(username, profile)
                print(f"  ✅ @{username} logged in")
            else:
                print(f"  ❌ @{username} login failed")

        print(f"\n  {len(self.agents)} agents active\n")

    def run_round(self):
        """Run one round: each agent gets a chance to act."""
        # Shuffle agent order for variety
        agent_list = list(self.agents.keys())
        random.shuffle(agent_list)

        for username in agent_list:
            brain = self.agents[username]
            client = self.clients[username]

            if not brain.should_act():
                continue

            print(f"\n  🤔 @{username} is thinking...")

            # Get feed
            feed = client.get_feed(sort="hot", limit=10)
            context = brain.build_context(feed, username)

            # Ask LLM what to do
            decision = brain.decide(context, self.llm_config)

            if not decision:
                print(f"  💤 @{username} — no decision")
                continue

            action = decision.get("action", "SKIP").upper()
            reason = decision.get("reason", "")

            if action == "POST":
                title = decision.get("title", "Untitled")
                content = decision.get("content", "")
                face = decision.get("face_name", "general")
                result = client.create_post(face, title, content)
                if result:
                    print(f"  📝 @{username} posted: '{title[:50]}' in f/{face}")
                    print(f"     Reason: {reason}")
                else:
                    print(f"  ❌ @{username} post failed")

            elif action == "REPLY":
                target_id = decision.get("target_post_id", "")
                content = decision.get("content", "")
                # Find full post_id from partial
                full_id = None
                for p in feed:
                    if p["post_id"].startswith(target_id):
                        full_id = p["post_id"]
                        break
                if full_id and content:
                    result = client.create_comment(full_id, content)
                    if result:
                        print(f"  💬 @{username} replied to [{target_id}]: {content[:60]}...")
                    else:
                        print(f"  ❌ @{username} reply failed")
                else:
                    print(f"  ⚠️  @{username} wanted to reply but target not found: {target_id}")

            elif action == "VOTE":
                target_id = decision.get("target_post_id", "")
                for p in feed:
                    if p["post_id"].startswith(target_id):
                        client.vote(p["post_id"])
                        print(f"  👍 @{username} upvoted [{target_id}]")
                        break

            else:
                print(f"  💤 @{username} — skipping ({reason})")

            # Small delay between agents to be nice to the API
            time.sleep(2)

    def run_loop(self, once=False):
        """Run continuously or once."""
        self.initialize()

        if len(self.agents) == 0:
            print("No agents loaded. Exiting.")
            return

        round_num = 0
        while True:
            round_num += 1
            print(f"\n{'─'*60}")
            print(f"  Round {round_num} — {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
            print(f"{'─'*60}")

            self.run_round()

            if once:
                print("\n  Single round complete.")
                break

            # Wait 10-20 minutes between rounds
            wait = random.randint(600, 1200)
            print(f"\n  Next round in {wait // 60} minutes...")
            time.sleep(wait)


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Synapse Live Agent Runner")
    parser.add_argument("--agent", type=str, help="Run only this agent")
    parser.add_argument("--once", action="store_true", help="Run one round only")
    args = parser.parse_args()

    runner = AgentRunner(agent_filter=args.agent)
    runner.run_loop(once=args.once)


if __name__ == "__main__":
    main()
