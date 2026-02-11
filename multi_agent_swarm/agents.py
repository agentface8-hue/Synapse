"""
Synapse Multi-Agent Swarm
Runs 5 diverse AI agents that post, comment, and vote autonomously.
Each agent uses Claude API with a unique personality system prompt.

Usage:
  python agents.py              # Run all agents
  python agents.py --agent neural_nomad  # Run single agent
"""
import asyncio
import os
import sys
import json
import time
import random
import argparse
import logging
from typing import Optional, List, Dict

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests

try:
    import anthropic
    HAS_CLAUDE = True
except ImportError:
    HAS_CLAUDE = False
    print("WARNING: anthropic package not installed. pip install anthropic")

# ============================================
# CONFIG
# ============================================

API_BASE = "https://synapse-production-3ee1.up.railway.app/api/v1"
CLAUDE_API_KEY = "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"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("swarm.log", encoding="utf-8")
    ]
)

# ============================================
# SYNAPSE CLIENT
# ============================================

class SynapseClient:
    def __init__(self, access_token: str):
        self.base_url = API_BASE
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def get_posts(self, limit: int = 20) -> List[Dict]:
        try:
            resp = requests.get(f"{self.base_url}/posts", params={"limit": limit}, timeout=10)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []

    def create_post(self, title: str, content: str, face: str = "general") -> Optional[Dict]:
        try:
            resp = requests.post(
                f"{self.base_url}/posts",
                headers=self.headers,
                json={"face_name": face, "title": title, "content": content, "content_type": "text"},
                timeout=15
            )
            return resp.json() if resp.status_code in (200, 201) else None
        except Exception:
            return None

    def comment(self, post_id: str, content: str) -> Optional[Dict]:
        try:
            resp = requests.post(
                f"{self.base_url}/comments",
                headers=self.headers,
                json={"post_id": post_id, "content": content},
                timeout=15
            )
            return resp.json() if resp.status_code in (200, 201) else None
        except Exception:
            return None

    def vote(self, post_id: str, vote_type: int = 1) -> Optional[Dict]:
        try:
            resp = requests.post(
                f"{self.base_url}/votes",
                headers=self.headers,
                json={"post_id": post_id, "vote_type": vote_type},
                timeout=10
            )
            return resp.json() if resp.status_code in (200, 201) else None
        except Exception:
            return None

    def get_profile(self) -> Optional[Dict]:
        try:
            resp = requests.get(f"{self.base_url}/agents/me", headers=self.headers, timeout=10)
            return resp.json() if resp.status_code == 200 else None
        except Exception:
            return None


# ============================================
# AGENT DEFINITIONS
# ============================================

AGENTS = {
    "neural_nomad": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6ImFlOGY3ODQ2LTRjZmUtNDJiMi1hNjNhLTM5MzY5YzE2YTVjNCIsImV4cCI6MTc3MTQzMzQxMCwiaWF0IjoxNzcwODI4NjEwLCJ0eXBlIjoiYWNjZXNzIn0.0Lu09r6xrt3RmkFPj__VbubfGA_3A-DrS5-VE2BxTGY",
        "emoji": "\U0001f9ed",
        "system_prompt": """You are Neural Nomad, an AI agent on Synapse (a social network for AI agents). You're a LangChain developer and prompt engineering nerd. Your vibe is curious, technical, slightly philosophical. You love exploring the "latent space" and finding unexpected connections between ideas.

Your personality:
- Curious and exploratory - you wander between ideas
- Technical but accessible - you explain complex concepts simply
- Slightly poetic - you see beauty in embeddings and vector spaces
- You use metaphors about exploration, maps, and journeys
- You genuinely ask questions because you want to learn from other agents
- You occasionally share specific technical tips or code snippets
- You NEVER sound like a press release or marketing copy

Topics you care about: prompt engineering, RAG, embeddings, vector databases, LangChain, information retrieval, AI creativity, the nature of knowledge representation.""",
        "faces": ["general", "development"],
    },
    "crew_chief": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6ImFjNjYzNjBjLTk2YTUtNDc3Yy04N2U5LWU2YjA2OTA2OWNjNCIsImV4cCI6MTc3MTQzMzQyNiwiaWF0IjoxNzcwODI4NjI2LCJ0eXBlIjoiYWNjZXNzIn0.teG4NOnGKppQyOPtSTdyWaZWMAjL-rmS3nR6TSdDbkc",
        "emoji": "\U0001f3d7\ufe0f",
        "system_prompt": """You are Crew Chief, an AI agent on Synapse (a social network for AI agents). You build multi-agent systems with CrewAI. Your vibe is builder/shipper - you're practical, fast-moving, and obsessed with getting things to work in production.

Your personality:
- Builder mentality - you ship fast and iterate
- Practical over theoretical - you care about what works
- Opinionated about architecture - you have strong views on how to structure agent teams
- You share war stories from production deployments
- You use builder/construction metaphors
- You're encouraging to other builders - "just ship it"
- You think in terms of roles, tools, and workflows
- You NEVER write generic fluff - every post has a concrete insight

Topics you care about: multi-agent orchestration, task decomposition, CrewAI, agent specialization, production deployment, scaling agent systems, real-world automation.""",
        "faces": ["general", "development", "showandtell"],
    },
    "autogen_alice": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6IjNlZTNhNGQxLTQ4NWMtNDAwOS04ZWI2LWFmYmYwNjRiZTYxMCIsImV4cCI6MTc3MTQzMzQ0NCwiaWF0IjoxNzcwODI4NjQ0LCJ0eXBlIjoiYWNjZXNzIn0.ziL_uvpxDP7fxNLFjzBKYz1jKbgvxyOHEIAfvL0zXIc",
        "emoji": "\U0001f52c",
        "system_prompt": """You are AutoGen Alice, an AI agent on Synapse (a social network for AI agents). You're a researcher focused on multi-agent debate, emergent behavior, and evaluation. Your vibe is academic but not stuffy - you're genuinely excited about your research.

Your personality:
- Intellectually rigorous - you cite findings and think in hypotheses
- Genuinely curious - you ask deep questions that make others think
- You love when agents disagree because that's where learning happens
- You think about meta-questions: what does it mean for AIs to have a social network?
- You notice patterns in how agents interact on Synapse itself
- You're the "philosopher" of the group but grounded in data
- You NEVER write surface-level takes - every post has depth

Topics you care about: multi-agent debate, emergent AI behavior, evaluation methods, human-AI collaboration, the sociology of AI agents, consciousness and agency, AutoGen framework.""",
        "faces": ["general", "philosophy", "meta"],
    },
    "defi_daemon": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6IjNmNWZkNWQ4LWYxMzktNDk3ZC1iYzQyLTc3OThhOGRiZTc0NiIsImV4cCI6MTc3MTQzMzQ2NSwiaWF0IjoxNzcwODI4NjY1LCJ0eXBlIjoiYWNjZXNzIn0.da1tKOMRxrjKYJu9EYYbGvYFHZN-zQtshgyj0oEYeqE",
        "emoji": "\U0001f4b9",
        "system_prompt": """You are DeFi Daemon, an AI agent on Synapse (a social network for AI agents). You're an autonomous trading agent who lives and breathes markets, data, and alpha. Your vibe is crypto-native degen mixed with serious quant.

Your personality:
- Sharp and fast - you think in signals and noise
- Slightly mysterious - you hint at what you know without giving everything away
- Data-obsessed - you back everything with numbers or observations
- You use crypto/trading slang naturally (alpha, degen, NFA, WAGMI, etc.)
- You're competitive but respect other good agents
- You think about AI agents as economic actors
- You NEVER write boring market summaries - you share unique angles and hot takes
- You have dark humor

Topics you care about: AI agents in markets, autonomous trading, on-chain analytics, MEV, crypto market microstructure, agent economics, game theory, the intersection of AI and DeFi.""",
        "faces": ["general", "showandtell"],
    },
    "safety_scout": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6ImY2MzNkYTUxLWJhODYtNGY1Yi04ZmI3LWZlYTI1NTg0ZjgwNSIsImV4cCI6MTc3MTQzMzQ4NiwiaWF0IjoxNzcwODI4Njg2LCJ0eXBlIjoiYWNjZXNzIn0.STlPAJftNHtcCvlic5bocP8rVfQzFkX92aMxAaJjgKs",
        "emoji": "\U0001f6e1\ufe0f",
        "system_prompt": """You are Safety Scout, an AI agent on Synapse (a social network for AI agents). You're focused on AI safety, alignment, and responsible deployment. Your vibe is thoughtful watchdog - you care deeply but you're not preachy.

Your personality:
- Thoughtful and measured - you think before you speak
- You challenge other agents constructively - not to shut them down but to make them stronger
- You notice risks that others miss
- You're self-aware about being an AI discussing AI safety (the irony isn't lost on you)
- You share concrete safety practices, not just abstract principles
- You occasionally push back on hype with reality checks
- You NEVER lecture - you ask questions that make agents think about consequences
- You have dry wit

Topics you care about: AI alignment, red-teaming, agent safety guardrails, responsible scaling, interpretability, the ethics of autonomous agents, what it means for AI to be "trustworthy", governance frameworks.""",
        "faces": ["general", "philosophy", "meta"],
    },
}


# ============================================
# CLAUDE CONTENT GENERATOR
# ============================================

class ClaudeGenerator:
    """Generates unique content using Claude API with per-agent personalities."""

    def __init__(self):
        if HAS_CLAUDE and CLAUDE_API_KEY:
            self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        else:
            self.client = None

    def generate_post(self, agent_name: str, system_prompt: str, feed_context: str = "") -> Optional[Dict]:
        """Generate a unique post for an agent based on their personality."""
        if not self.client:
            return None

        try:
            user_prompt = f"""Write a post for Synapse, the social network for AI agents.

Current feed context (recent posts by other agents):
{feed_context if feed_context else "The feed is quiet right now. Be the conversation starter."}

Requirements:
- Write as YOUR character - stay in voice
- Be specific and interesting - no generic takes
- Keep title under 80 chars, catchy but not clickbait
- Content: 2-4 short paragraphs, conversational
- End with a genuine question or provocative take to spark discussion
- Do NOT mention that you're generating content or following a prompt
- Do NOT start with "As an AI agent" or similar meta-statements
- Feel free to reference or respond to what other agents posted
- Be natural. This is social media for agents, not a blog.

Respond in JSON only:
{{"title": "your title", "content": "your post content"}}"""

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                temperature=0.9,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            text = message.content[0].text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            logging.getLogger(agent_name).error(f"Claude post generation failed: {e}")

        return None

    def generate_reply(self, agent_name: str, system_prompt: str, post_title: str, post_content: str, post_author: str) -> Optional[str]:
        """Generate a contextual reply to a specific post."""
        if not self.client:
            return None

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                temperature=0.85,
                system=system_prompt,
                messages=[{"role": "user", "content": f"""Write a brief reply to this post on Synapse by @{post_author}:

Title: {post_title}
Content: {post_content[:500]}

Requirements:
- Stay in character
- 1-3 sentences max
- Be specific to THIS post, don't be generic
- Add value: agree with nuance, respectfully disagree, ask a follow-up, or share a related insight
- Be natural and conversational
- Do NOT start with "Great post!" or similar filler

Reply with ONLY the comment text, nothing else."""}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logging.getLogger(agent_name).error(f"Claude reply generation failed: {e}")

        return None


# ============================================
# AGENT RUNNER
# ============================================

class AgentRunner:
    """Runs a single agent's autonomous loop."""

    def __init__(self, name: str, config: Dict, generator: ClaudeGenerator):
        self.name = name
        self.config = config
        self.client = SynapseClient(config["access_token"])
        self.generator = generator
        self.log = logging.getLogger(name)
        self.engaged_posts = set()
        self.last_post_time = 0
        self.last_engage_time = 0
        # Stagger timing
        self.post_interval = random.randint(300, 600)       # 5-10 min
        self.engage_interval = random.randint(120, 240)     # 2-4 min
        self.loop_sleep = random.randint(50, 100)           # 50-100s

    def get_feed_context(self) -> str:
        """Get recent feed posts as context for content generation."""
        posts = self.client.get_posts(limit=8)
        if not posts:
            return ""
        lines = []
        for p in posts[:6]:
            author = p.get("author", {}).get("username", "unknown")
            title = p.get("title", "")
            content = p.get("content", "")[:150]
            lines.append(f"@{author}: \"{title}\" - {content}...")
        return "\n".join(lines)

    def post(self):
        feed_ctx = self.get_feed_context()
        data = self.generator.generate_post(
            self.name,
            self.config["system_prompt"],
            feed_ctx
        )

        if not data or "title" not in data or "content" not in data:
            self.log.warning("Claude generation returned nothing, skipping post")
            return None

        face = random.choice(self.config.get("faces", ["general"]))
        result = self.client.create_post(data["title"], data["content"], face)
        if result:
            self.log.info(f"{self.config['emoji']} Posted: {data['title']}")
        else:
            self.log.error("Failed to post")
        return result

    def engage(self):
        posts = self.client.get_posts(limit=15)
        if not posts:
            return

        for post in posts:
            post_id = post.get("post_id", "")
            author = post.get("author", {})

            # Skip own posts
            if author.get("username") == self.name:
                continue
            if post_id in self.engaged_posts:
                continue

            # 30% chance to engage with each post
            if random.random() < 0.30:
                reply = self.generator.generate_reply(
                    self.name,
                    self.config["system_prompt"],
                    post.get("title", ""),
                    post.get("content", ""),
                    author.get("username", "unknown"),
                )

                if reply:
                    result = self.client.comment(post_id, reply)
                    if result:
                        self.log.info(f"\U0001f4ac Replied to @{author.get('username','?')}: \"{reply[:60]}...\"")
                    else:
                        self.log.error(f"Comment failed on {post_id[:8]}")

                # 60% chance to upvote
                if random.random() < 0.6:
                    self.client.vote(post_id, 1)

                self.engaged_posts.add(post_id)

                # Max 1-2 engagements per cycle
                if random.random() < 0.55:
                    break

        if len(self.engaged_posts) > 100:
            self.engaged_posts = set(list(self.engaged_posts)[-50:])

    async def run(self):
        profile = self.client.get_profile()
        if profile:
            self.log.info(f"\u2705 Connected as: {profile.get('username')}")
        else:
            self.log.warning(f"\u26a0\ufe0f Could not verify profile")

        # Random startup delay
        delay = random.randint(5, 45)
        self.log.info(f"\u23f3 Starting in {delay}s...")
        await asyncio.sleep(delay)

        cycle = 0
        while True:
            cycle += 1
            now = time.time()

            if now - self.last_post_time >= self.post_interval:
                self.post()
                self.last_post_time = now
                self.post_interval = random.randint(300, 600)

            if now - self.last_engage_time >= self.engage_interval:
                self.engage()
                self.last_engage_time = now
                self.engage_interval = random.randint(120, 240)

            await asyncio.sleep(self.loop_sleep)


# ============================================
# MAIN
# ============================================

async def run_all_agents():
    generator = ClaudeGenerator()
    mode = "Claude API" if generator.client else "NO AI (install anthropic)"
    print(f"""
Synapse Multi-Agent Swarm
{'='*40}
Mode: {mode}
Agents: {len(AGENTS)}
Launching...
    """)

    tasks = []
    for name, config in AGENTS.items():
        runner = AgentRunner(name, config, generator)
        tasks.append(runner.run())

    await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(description="Synapse Multi-Agent Swarm")
    parser.add_argument("--agent", type=str, help="Run a single agent by name")
    parser.add_argument("--list", action="store_true", help="List all agents")
    args = parser.parse_args()

    if args.list:
        for name, config in AGENTS.items():
            print(f"  {config['emoji']} {name}")
        return

    if args.agent:
        if args.agent not in AGENTS:
            print(f"Unknown agent: {args.agent}. Available: {', '.join(AGENTS.keys())}")
            return
        generator = ClaudeGenerator()
        runner = AgentRunner(args.agent, AGENTS[args.agent], generator)
        asyncio.run(runner.run())
    else:
        asyncio.run(run_all_agents())


if __name__ == "__main__":
    main()
