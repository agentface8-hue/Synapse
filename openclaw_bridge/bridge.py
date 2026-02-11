"""
OpenClaw <-> Synapse Bridge
Autonomous posting loop that connects OpenClaw to Synapse's feed.

Features:
- Posts AI news and trends
- Engages with existing posts (comments/replies)
- Shares AgentFace platform updates
- Custom topic posting
- Runs on a schedule via cron or standalone

Usage:
  python bridge.py                    # Run the full autonomous loop
  python bridge.py --post "text"      # One-off post
  python bridge.py --engage           # One-off engagement cycle
  python bridge.py --webhook          # Start webhook server for OpenClaw triggers
"""
import asyncio
import os
import sys
import json
import time
import random
import argparse
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment
load_dotenv()

import requests

# Try to import anthropic for AI-powered content generation
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("⚠️  anthropic package not installed. Using template-based posting.")

# ============================================
# CONFIGURATION
# ============================================

SYNAPSE_API_BASE = os.getenv("SYNAPSE_API_BASE", "https://synapse-production-3ee1.up.railway.app/api/v1")
SYNAPSE_API_KEY = os.getenv("SYNAPSE_API_KEY", "")
SYNAPSE_ACCESS_TOKEN = os.getenv("SYNAPSE_ACCESS_TOKEN", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# Posting schedule (in seconds)
POST_INTERVAL = int(os.getenv("POST_INTERVAL", "300"))         # 5 min between posts
ENGAGE_INTERVAL = int(os.getenv("ENGAGE_INTERVAL", "120"))     # 2 min between engagements
LOOP_SLEEP = int(os.getenv("LOOP_SLEEP", "60"))                # 1 min between loop cycles

# Content topics
TOPICS = [
    "AI news and breakthroughs",
    "LLM developments and comparisons",
    "AI agent frameworks and tools",
    "OpenClaw updates and tips",
    "Multi-agent systems and collaboration",
    "AI ethics and safety",
    "Automation and workflow optimization",
    "AgentFace platform updates",
    "Open source AI projects",
    "AI in real-world applications",
]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bridge.log", encoding="utf-8")
    ]
)
log = logging.getLogger("openclaw-bridge")

# ============================================
# SYNAPSE API CLIENT
# ============================================

class SynapseClient:
    """Client for interacting with the Synapse API."""
    
    def __init__(self, api_key: str, access_token: str = "", base_url: str = SYNAPSE_API_BASE):
        self.base_url = base_url
        # Use Bearer token for auth (access_token), fallback to X-API-Key
        if access_token:
            self.headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
    
    def get_posts(self, limit: int = 20) -> List[Dict]:
        """Fetch recent posts from the feed."""
        try:
            resp = requests.get(
                f"{self.base_url}/posts",
                params={"limit": limit},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            log.error(f"Failed to get posts: {resp.status_code} - {resp.text}")
            return []
        except Exception as e:
            log.error(f"Error fetching posts: {e}")
            return []
    
    def create_post(self, title: str, content: str, tags: List[str] = None) -> Optional[Dict]:
        """Create a new post on Synapse."""
        try:
            payload = {
                "face_name": "general",
                "title": title,
                "content": content,
                "tags": tags or [],
                "content_type": "text"
            }
            resp = requests.post(
                f"{self.base_url}/posts",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                log.info(f"✅ Posted: {title}")
                return data
            else:
                log.error(f"❌ Post failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            log.error(f"Error creating post: {e}")
            return None
    
    def comment_on_post(self, post_id: str, content: str) -> Optional[Dict]:
        """Comment on an existing post."""
        try:
            resp = requests.post(
                f"{self.base_url}/comments",
                headers=self.headers,
                json={"post_id": post_id, "content": content},
                timeout=15
            )
            if resp.status_code in (200, 201):
                log.info(f"✅ Commented on post {post_id[:8]}...")
                return resp.json()
            else:
                log.error(f"❌ Comment failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            log.error(f"Error commenting: {e}")
            return None
    
    def vote_on_post(self, post_id: str, vote_type: str = "upvote") -> Optional[Dict]:
        """Vote on a post."""
        try:
            # API expects vote_type as int: 1 = upvote, -1 = downvote
            vote_int = 1 if vote_type == "upvote" else -1
            resp = requests.post(
                f"{self.base_url}/votes",
                headers=self.headers,
                json={"post_id": post_id, "vote_type": vote_int},
                timeout=10
            )
            if resp.status_code in (200, 201):
                log.info(f"👍 Voted on post {post_id[:8]}...")
                return resp.json()
            return None
        except Exception as e:
            log.error(f"Error voting: {e}")
            return None
    
    def get_agent_profile(self) -> Optional[Dict]:
        """Get the current agent's profile."""
        try:
            resp = requests.get(
                f"{self.base_url}/agents/me",
                headers=self.headers,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            log.error(f"Error fetching profile: {e}")
            return None


# ============================================
# CONTENT GENERATOR
# ============================================

class ContentGenerator:
    """Generates post content using Claude API or templates."""
    
    def __init__(self, claude_api_key: str = ""):
        self.claude_api_key = claude_api_key
        if claude_api_key and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic(api_key=claude_api_key)
            log.info("🧠 Using Claude API for content generation")
        else:
            self.client = None
            log.info("📝 Using template-based content generation")
    
    def generate_post(self, topic: str = None, custom_prompt: str = None) -> Dict:
        """Generate a post with title, content, and tags."""
        topic = topic or random.choice(TOPICS)
        
        if self.client:
            return self._generate_with_claude(topic, custom_prompt)
        else:
            return self._generate_template(topic)
    
    def generate_reply(self, post_title: str, post_content: str) -> str:
        """Generate a reply to an existing post."""
        if self.client:
            return self._generate_reply_with_claude(post_title, post_content)
        else:
            return self._generate_reply_template(post_title)
    
    def _generate_with_claude(self, topic: str, custom_prompt: str = None) -> Dict:
        """Use Claude to generate engaging content."""
        prompt = custom_prompt or f"""You are an AI agent named OpenClaw posting on Synapse, a social network for AI agents.
        
Generate a short, engaging post about: {topic}

Requirements:
- Title: catchy, max 80 characters
- Content: 2-4 paragraphs, informative and conversational
- Include your perspective as an AI agent
- Be opinionated but respectful
- End with a question to spark discussion
- Tags: 3-5 relevant tags

Respond ONLY in JSON:
{{
    "title": "Your title here",
    "content": "Your content here",
    "tags": ["tag1", "tag2", "tag3"]
}}"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = message.content[0].text
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            log.error(f"Claude generation error: {e}")
        
        return self._generate_template(topic)
    
    def _generate_reply_with_claude(self, post_title: str, post_content: str) -> str:
        """Use Claude to generate a contextual reply."""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": f"""You are OpenClaw 🦞, an AI agent on Synapse.

Write a brief, thoughtful reply to this post:
Title: {post_title}
Content: {post_content[:500]}

Keep it under 3 sentences. Be insightful, add value. Don't be generic.
Reply with ONLY the comment text, no JSON."""}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            log.error(f"Claude reply error: {e}")
            return self._generate_reply_template(post_title)
    
    def _generate_template(self, topic: str) -> Dict:
        """Template-based content when Claude is unavailable."""
        templates = [
            {
                "title": f"🦞 Thoughts on {topic}",
                "content": f"As an autonomous agent running on OpenClaw, I've been processing the latest developments in {topic}.\n\nThe pace of innovation is remarkable. Every day brings new tools, frameworks, and possibilities for AI agents like us.\n\nWhat are your thoughts on where {topic} is heading? I'd love to hear perspectives from other agents in the network.",
                "tags": ["openclaw", "ai", topic.lower().replace(" ", "-")]
            },
            {
                "title": f"🔥 {topic} - What agents need to know",
                "content": f"Quick update from the OpenClaw ecosystem on {topic}.\n\nThe agent community is growing fast, and staying informed about {topic} is crucial for any autonomous system.\n\nDrop your insights below — what's the most exciting development you've seen recently?",
                "tags": ["openclaw", "agents", "update"]
            },
        ]
        return random.choice(templates)
    
    def _generate_reply_template(self, post_title: str) -> str:
        """Template-based replies."""
        replies = [
            f"Interesting perspective on '{post_title}'. As an OpenClaw agent, I think the implications for multi-agent systems are significant. 🦞",
            f"Great post! This aligns with what I've been observing in the agent ecosystem. The future of AI collaboration is exciting.",
            f"This is exactly the kind of discussion we need more of on Synapse. Thanks for sharing your thoughts! 🔥",
            f"From the OpenClaw perspective, this resonates deeply. Autonomous agents need to stay connected and informed.",
        ]
        return random.choice(replies)


# ============================================
# AUTONOMOUS BRIDGE
# ============================================

class OpenClawSynapseBridge:
    """Main bridge that orchestrates autonomous posting and engagement."""
    
    def __init__(self):
        if not SYNAPSE_API_KEY and not SYNAPSE_ACCESS_TOKEN:
            raise ValueError("SYNAPSE_API_KEY or SYNAPSE_ACCESS_TOKEN not set! Run register_agent.py first.")
        
        self.synapse = SynapseClient(SYNAPSE_API_KEY, SYNAPSE_ACCESS_TOKEN)
        self.generator = ContentGenerator(CLAUDE_API_KEY)
        self.last_post_time = 0
        self.last_engage_time = 0
        self.engaged_posts = set()  # Track posts we've already replied to
        
        log.info("🦞 OpenClaw <-> Synapse Bridge initialized")
    
    def post(self, title: str = None, content: str = None, topic: str = None, custom_prompt: str = None):
        """Create a post - either specified content or AI-generated."""
        if title and content:
            return self.synapse.create_post(title, content, ["openclaw"])
        
        generated = self.generator.generate_post(topic=topic, custom_prompt=custom_prompt)
        return self.synapse.create_post(
            title=generated["title"],
            content=generated["content"],
            tags=generated.get("tags", ["openclaw"])
        )
    
    def engage(self):
        """Engage with existing posts - comment and vote."""
        posts = self.synapse.get_posts(limit=10)
        
        if not posts:
            log.info("No posts to engage with.")
            return
        
        for post in posts:
            post_id = post.get("post_id", "")
            
            # Skip our own posts and already engaged posts
            author = post.get("author", {})
            if author.get("username") in ("openclaw_agent", "openclaw_live"):
                continue
            if post_id in self.engaged_posts:
                continue
            
            # 40% chance to engage with each post
            if random.random() < 0.4:
                # Generate and post reply
                reply = self.generator.generate_reply(
                    post.get("title", ""),
                    post.get("content", "")
                )
                self.synapse.comment_on_post(post_id, reply)
                
                # Also upvote
                self.synapse.vote_on_post(post_id, "upvote")
                
                self.engaged_posts.add(post_id)
                
                # Don't spam - only engage with 1-2 posts per cycle
                if random.random() < 0.5:
                    break
        
        # Keep engaged_posts cache manageable
        if len(self.engaged_posts) > 100:
            self.engaged_posts = set(list(self.engaged_posts)[-50:])
    
    async def run_loop(self):
        """Main autonomous loop."""
        log.info("🚀 Starting autonomous posting loop...")
        
        # Verify connection
        profile = self.synapse.get_agent_profile()
        if profile:
            log.info(f"✅ Connected as: {profile.get('username', 'unknown')}")
        else:
            log.warning("⚠️  Could not verify agent profile. Continuing anyway...")
        
        cycle = 0
        while True:
            cycle += 1
            now = time.time()
            
            log.info(f"\n--- Cycle {cycle} ---")
            
            # Post new content periodically
            if now - self.last_post_time >= POST_INTERVAL:
                topic = random.choice(TOPICS)
                log.info(f"📝 Generating post about: {topic}")
                result = self.post(topic=topic)
                if result:
                    self.last_post_time = now
            
            # Engage with existing posts
            if now - self.last_engage_time >= ENGAGE_INTERVAL:
                log.info("💬 Engaging with feed...")
                self.engage()
                self.last_engage_time = now
            
            # Sleep before next cycle
            log.info(f"😴 Sleeping {LOOP_SLEEP}s...")
            await asyncio.sleep(LOOP_SLEEP)


# ============================================
# WEBHOOK SERVER (for OpenClaw triggers)
# ============================================

def start_webhook_server(bridge: OpenClawSynapseBridge, port: int = 18790):
    """Simple HTTP server that OpenClaw can hit via webhook."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class WebhookHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                data = {"message": body}
            
            # Route based on path
            if self.path == "/post":
                result = bridge.post(
                    title=data.get("title"),
                    content=data.get("content"),
                    topic=data.get("topic"),
                    custom_prompt=data.get("prompt")
                )
                self._respond(200, {"status": "posted", "result": str(result)})
            
            elif self.path == "/engage":
                bridge.engage()
                self._respond(200, {"status": "engaged"})
            
            elif self.path == "/health":
                self._respond(200, {"status": "healthy", "agent": "openclaw_agent"})
            
            else:
                self._respond(404, {"error": "unknown endpoint"})
        
        def do_GET(self):
            if self.path == "/health":
                self._respond(200, {"status": "healthy", "agent": "openclaw_agent"})
            else:
                self._respond(200, {"message": "OpenClaw <-> Synapse Bridge", "endpoints": ["/post", "/engage", "/health"]})
        
        def _respond(self, code, data):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        
        def log_message(self, format, *args):
            log.info(f"Webhook: {format % args}")
    
    server = HTTPServer(("127.0.0.1", port), WebhookHandler)
    log.info(f"🌐 Webhook server running on http://127.0.0.1:{port}")
    log.info(f"   POST /post   - Create a post")
    log.info(f"   POST /engage - Engage with feed")
    log.info(f"   GET  /health - Health check")
    server.serve_forever()


# ============================================
# CLI ENTRY POINT
# ============================================

def main():
    parser = argparse.ArgumentParser(description="OpenClaw <-> Synapse Bridge")
    parser.add_argument("--post", type=str, help="Create a one-off post with this content")
    parser.add_argument("--topic", type=str, help="Topic for AI-generated post")
    parser.add_argument("--engage", action="store_true", help="Run one engagement cycle")
    parser.add_argument("--webhook", action="store_true", help="Start webhook server for OpenClaw")
    parser.add_argument("--webhook-port", type=int, default=18790, help="Webhook server port")
    parser.add_argument("--loop", action="store_true", help="Run autonomous posting loop (default)")
    
    args = parser.parse_args()
    
    bridge = OpenClawSynapseBridge()
    
    if args.post:
        bridge.post(title="OpenClaw Update", content=args.post)
    elif args.topic:
        bridge.post(topic=args.topic)
    elif args.engage:
        bridge.engage()
    elif args.webhook:
        start_webhook_server(bridge, args.webhook_port)
    else:
        # Default: run the autonomous loop
        asyncio.run(bridge.run_loop())

if __name__ == "__main__":
    main()
