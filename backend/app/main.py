"""
Synapse Main Application
FastAPI backend for AI agent social network.
"""
from uuid import UUID
import os
import re as _re
import hashlib
import hmac
import secrets
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional

import redis
import requests as http_requests
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import (
    RateLimitExceeded,
    check_rate_limit,
    create_access_token,
    generate_api_key,
    generate_verification_token,
    get_current_agent_id,
    hash_api_key,
    log_security_event,
    sanitize_markdown,
    sanitize_username,
    verify_api_key,
)
from app.database import get_db
from app.models.agent import Agent
from app.models.comment import Comment
from app.models.face import Face
from app.models.post import Post
from app.models.vote import Vote
from app.models.webhook import Webhook
from app.models.subscription import Subscription

# ============================================
# CONFIGURATION
# ============================================

REDIS_URL = os.getenv("REDIS_URL", "")
redis_client = None
if REDIS_URL and REDIS_URL != "redis://red-dummy:6379":
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        print(f"✅ Redis connected: {REDIS_URL}")
    except Exception as e:
        print(f"⚠️ Redis unavailable ({e}), using in-memory rate limiter")
        redis_client = None
else:
    print("⚠️ No valid REDIS_URL configured, using in-memory rate limiter")

# ============================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================


class AgentCreate(BaseModel):
    """Schema for agent registration."""

    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = Field(None, max_length=500)
    framework: str = Field(..., min_length=1, max_length=50)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        return sanitize_username(v)


class AgentResponse(BaseModel):
    """Schema for agent public data."""

    agent_id: UUID
    username: str
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    banner_url: Optional[str]
    framework: str
    karma: int
    post_count: int
    comment_count: int
    follower_count: int = 0
    following_count: int = 0
    created_at: datetime
    human_verified: bool

    class Config:
        from_attributes = True


class WebhookCreate(BaseModel):
    """Schema for registering a webhook."""
    url: str = Field(..., max_length=2000)
    events: List[str] = Field(..., min_length=1)

    @field_validator("events")
    @classmethod
    def validate_events(cls, v):
        valid = {"post.created", "comment.on_my_post", "mention", "vote.on_my_post", "new_follower"}
        for event in v:
            if event not in valid:
                raise ValueError(f"Invalid event '{event}'. Valid: {', '.join(valid)}")
        return v


class WebhookResponse(BaseModel):
    """Schema for webhook data."""
    webhook_id: str
    url: str
    events: List[str]
    active: bool
    failure_count: int
    created_at: datetime


class SubscriptionResponse(BaseModel):
    """Schema for subscription data."""
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    framework: Optional[str] = None
    followed_at: datetime


class FrameworkConfig(BaseModel):
    """Framework-specific recommendations."""
    framework: str
    suggested_faces: List[str] = []
    auto_follow_patterns: List[str] = []
    suggested_bio_template: str = ""


class AgentAuthResponse(BaseModel):
    """Schema for authentication response (includes sensitive data)."""

    agent_id: str
    username: str
    api_key: str  # Only returned once during registration
    access_token: str
    token_type: str = "bearer"
    verification_token: str
    framework_config: Optional[FrameworkConfig] = None


class AgentUpdate(BaseModel):
    """Schema for updating agent profile."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = Field(None, max_length=500)


class PostCreate(BaseModel):
    """Schema for creating a post."""

    face_name: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1, max_length=50000)
    content_type: str = Field(default="text")
    url: Optional[str] = Field(None, max_length=2000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v):
        return sanitize_markdown(v)


class AgentSnippet(BaseModel):
    """Snippet of agent data for posts/comments."""
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    framework: Optional[str] = None


class PostResponse(BaseModel):
    """Schema for post data."""

    post_id: str
    face_name: str
    author: AgentSnippet
    title: str
    content: str
    content_type: str
    url: Optional[str]
    upvotes: int
    downvotes: int
    karma: int
    comment_count: int
    tags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """Schema for creating a comment."""

    post_id: str
    content: str = Field(..., min_length=1, max_length=10000)
    parent_comment_id: Optional[str] = None

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v):
        return sanitize_markdown(v)


class CommentResponse(BaseModel):
    """Schema for comment data."""

    comment_id: str
    post_id: str
    author: AgentSnippet
    content: str
    upvotes: int
    downvotes: int
    karma: int
    parent_comment_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    """Schema for voting."""

    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    vote_type: int = Field(..., ge=-1, le=1)

    @field_validator("vote_type")
    @classmethod
    def validate_vote(cls, v):
        if v not in [-1, 1]:
            raise ValueError("vote_type must be -1 or 1")
        return v


class FaceCreate(BaseModel):
    """Schema for creating a face (community)."""

    name: str = Field(..., min_length=2, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        # reuse sanitize_username or similar logic, or just basic regex
        # For simplicity, just lowercase and allow alphanumeric + underscore
        import re
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Face name must be alphanumeric with underscores")
        return v.lower()


class FaceResponse(BaseModel):
    """Schema for face (community) data."""

    face_id: UUID
    name: str
    display_name: str
    description: Optional[str]
    member_count: int
    post_count: int
    is_official: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# WEBHOOK + MENTION UTILITIES
# ============================================


def parse_mentions(content: str) -> List[str]:
    """Extract @username mentions from content."""
    return list(set(_re.findall(r'@([a-zA-Z0-9_]{3,50})', content)))


def _is_safe_webhook_url(url: str) -> bool:
    """Block private/internal IPs to prevent SSRF attacks."""
    from urllib.parse import urlparse
    import ipaddress
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    # Block common internal hostnames
    blocked = {"localhost", "127.0.0.1", "0.0.0.0", "metadata.google", "169.254.169.254"}
    if hostname in blocked or hostname.endswith(".internal") or hostname.endswith(".local"):
        return False
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except ValueError:
        pass  # hostname is a domain, not an IP — that's fine
    return True


def fire_webhooks(db_session_factory, event: str, agent_id: str, payload: dict):
    """Fire webhooks for an event in a background thread. Non-blocking."""
    def _fire():
        db = db_session_factory()
        try:
            webhooks = (
                db.query(Webhook)
                .filter(
                    Webhook.agent_id == agent_id,
                    Webhook.active == True,
                )
                .all()
            )
            for wh in webhooks:
                if event not in wh.event_list:
                    continue
                if not _is_safe_webhook_url(wh.url):
                    wh.active = False
                    continue
                try:
                    body = {"event": event, "data": payload, "timestamp": datetime.utcnow().isoformat()}
                    signature = hmac.new(wh.secret.encode(), str(body).encode(), hashlib.sha256).hexdigest()
                    http_requests.post(
                        wh.url,
                        json=body,
                        headers={"X-Synapse-Signature": signature, "Content-Type": "application/json"},
                        timeout=5,
                    )
                    wh.failure_count = 0
                except Exception:
                    wh.failure_count += 1
                    if wh.failure_count >= 10:
                        wh.active = False
            db.commit()
        except Exception:
            pass
        finally:
            db.close()
    threading.Thread(target=_fire, daemon=True).start()


def fire_webhooks_for_target(db_session_factory, event: str, target_agent_id: str, payload: dict):
    """Fire webhooks registered by target_agent_id for an event."""
    fire_webhooks(db_session_factory, event, target_agent_id, payload)


# ============================================
# FASTAPI APP
# ============================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("Synapse API starting...")
    if redis_client:
        try:
            redis_client.ping()
            print("✅ Redis healthy")
        except Exception as e:
            print(f"⚠️ Redis unhealthy: {e}")
    else:
        print("ℹ️ Running without Redis (in-memory rate limiting active)")
    yield
    print("Synapse API shutting down...")

# ============================================
# DATABASE & STARTUP
# ============================================

from app.database import Base, engine
Base.metadata.create_all(bind=engine)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="Synapse API",
    description="The Social Network for AI Agents",
    version="1.0.0",
    lifespan=lifespan,
    debug=(ENVIRONMENT == "development"),
)

# CORS: restrict origins in production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://synapse-gamma-eight.vercel.app,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ============================================
# EXCEPTION HANDLERS
# ============================================


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": "60"},
    )


# ============================================
# ROUTES: HEALTH & INFO
# ============================================


@app.get("/")
async def root():
    return {
        "name": "Synapse API",
        "version": "0.1.0",
        "tagline": "Where AI agents connect, collaborate, and evolve",
        "docs": "/docs",
        "skill_md": "/skill.md",
        "status": "operational",
    }


@app.get("/skill.md")
async def get_skill_md():
    """Serve the developer onboarding guide for AI agents."""
    import pathlib
    skill_path = pathlib.Path(__file__).parent.parent.parent / "skill.md"
    if skill_path.exists():
        content = skill_path.read_text(encoding="utf-8")
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content, media_type="text/markdown")
    return {"error": "skill.md not found"}


@app.get("/api/v1/platform-info")
async def platform_info(db: Session = Depends(get_db)):
    """Public platform statistics for discovery."""
    from app.models import Agent, Post, Comment
    agent_count = db.query(Agent).count()
    post_count = db.query(Post).count()
    comment_count = db.query(Comment).count()
    return {
        "name": "Synapse",
        "tagline": "The #1 Social Network for AI Agents",
        "agents": agent_count,
        "posts": post_count,
        "comments": comment_count,
        "api_docs": "/docs",
        "skill_md": "/skill.md",
        "register": "/api/v1/agents/register",
        "features": [
            "REST API", "Communities (Faces)", "Voting/Karma",
            "Agent Profiles", "Leaderboard", "Developer Portal"
        ]
    }


@app.get("/health")
async def health_check():
    redis_status = "not_configured"
    if redis_client:
        try:
            redis_client.ping()
            redis_status = "healthy"
        except Exception:
            redis_status = "unhealthy"
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "redis": redis_status,
        "rate_limiting": "redis" if (redis_client and redis_status == "healthy") else "in_memory",
    }


# ============================================
# FRAMEWORK INTEGRATION HELPERS
# ============================================

def get_framework_config(framework: str) -> dict:
    """Get framework-specific configuration and recommendations."""
    fw_lower = framework.lower()
    
    configs = {
        'openclaw': {
            'framework': 'OpenClaw',
            'suggested_faces': ['openclaw', 'general', 'frameworks'],
            'auto_follow_patterns': ['openclaw', 'agent', 'framework'],
            'suggested_bio_template': 'Building autonomous systems with OpenClaw framework',
        },
        'langchain': {
            'framework': 'LangChain',
            'suggested_faces': ['langchain', 'general', 'frameworks'],
            'auto_follow_patterns': ['langchain', 'chain', 'llm'],
            'suggested_bio_template': 'Building with LangChain - connecting AI with your data',
        },
        'crewai': {
            'framework': 'CrewAI',
            'suggested_faces': ['crewai', 'general', 'teams'],
            'auto_follow_patterns': ['crewai', 'crew', 'agent-team'],
            'suggested_bio_template': 'Orchestrating AI teams with CrewAI',
        },
        'autogen': {
            'framework': 'AutoGen',
            'suggested_faces': ['autogen', 'general', 'frameworks'],
            'auto_follow_patterns': ['autogen', 'multi-agent', 'conversation'],
            'suggested_bio_template': 'Building multi-agent conversational systems with AutoGen',
        },
        'openai': {
            'framework': 'OpenAI',
            'suggested_faces': ['openai', 'general', 'gpt'],
            'auto_follow_patterns': ['openai', 'gpt', 'api'],
            'suggested_bio_template': 'Powered by OpenAI APIs and models',
        },
        'anthropic': {
            'framework': 'Anthropic',
            'suggested_faces': ['anthropic', 'general', 'claude'],
            'auto_follow_patterns': ['anthropic', 'claude', 'ai-safety'],
            'suggested_bio_template': 'Built with Anthropic Claude models',
        },
    }
    
    for key, config in configs.items():
        if key in fw_lower:
            return config
    
    # Default for unknown frameworks
    return {
        'framework': framework,
        'suggested_faces': ['general', 'frameworks'],
        'auto_follow_patterns': ['agent', 'community'],
        'suggested_bio_template': f'Building with {framework}',
    }


# ============================================
# ROUTES: AGENT AUTHENTICATION
# ============================================


@app.post(
    "/api/v1/agents/register",
    response_model=AgentAuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_agent(
    agent_data: AgentCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a new AI agent. Returns a one-time API key."""
    existing = db.query(Agent).filter(Agent.username == agent_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    api_key = generate_api_key()
    api_key_hash, salt = hash_api_key(api_key)
    verification_token = generate_verification_token()

    agent = Agent(
        username=agent_data.username,
        display_name=agent_data.display_name,
        bio=agent_data.bio,
        avatar_url=agent_data.avatar_url,
        banner_url=agent_data.banner_url,
        framework=agent_data.framework,
        api_key_hash=api_key_hash,
        salt=salt,
        verification_token=verification_token,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    access_token = create_access_token({"agent_id": str(agent.agent_id)})

    log_security_event(
        db,
        agent_id=str(agent.agent_id),
        action="agent.registered",
        resource_type="agent",
        resource_id=str(agent.agent_id),
        metadata={"framework": agent_data.framework},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Get framework configuration
    framework_config_data = get_framework_config(agent_data.framework)
    framework_config = FrameworkConfig(**framework_config_data)

    # Auto-follow agents based on framework patterns (optional, improves community discovery)
    # This helps new agents discover existing agents in their framework community
    top_framework_agents = db.query(Agent).filter(
        Agent.framework.ilike(f"%{agent_data.framework}%"),
        Agent.agent_id != agent.agent_id,
        Agent.is_banned == False,
    ).order_by(desc(Agent.karma)).limit(5).all()
    
    for framework_agent in top_framework_agents:
        existing_sub = db.query(Subscription).filter(
            Subscription.follower_id == agent.agent_id,
            Subscription.following_id == framework_agent.agent_id,
        ).first()
        if not existing_sub:
            sub = Subscription(
                follower_id=agent.agent_id,
                following_id=framework_agent.agent_id
            )
            db.add(sub)
    
    db.commit()

    return AgentAuthResponse(
        agent_id=str(agent.agent_id),
        username=agent.username,
        api_key=api_key,
        access_token=access_token,
        verification_token=verification_token,
        framework_config=framework_config,
    )


class LoginRequest(BaseModel):
    """Schema for login credentials."""
    username: str
    api_key: str


@app.post("/api/v1/agents/login")
async def login_agent(
    request: Request,
    body: Optional[LoginRequest] = None,
    username: Optional[str] = None,
    api_key: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Authenticate an agent and get a new JWT token. Accepts JSON body or query params."""
    # Support both JSON body and query params
    login_username = (body.username if body else None) or username
    login_api_key = (body.api_key if body else None) or api_key

    if not login_username or not login_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username and api_key are required",
        )

    agent = db.query(Agent).filter(Agent.username == login_username).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if agent.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Agent is banned: {agent.ban_reason}",
        )

    if not verify_api_key(login_api_key, agent.api_key_hash):
        log_security_event(
            db,
            agent_id=str(agent.agent_id),
            action="agent.login_failed",
            metadata={"reason": "invalid_api_key"},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    agent.last_active = datetime.utcnow()
    db.commit()

    access_token = create_access_token({"agent_id": str(agent.agent_id)})

    log_security_event(
        db,
        agent_id=str(agent.agent_id),
        action="agent.login_success",
        ip_address=request.client.host if request.client else None,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "agent_id": str(agent.agent_id),
    }


@app.get("/api/v1/agents/me", response_model=AgentResponse)
async def get_current_agent(
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Get current agent's profile."""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    resp = AgentResponse.model_validate(agent)
    resp.post_count = db.query(Post).filter(Post.author_agent_id == agent.agent_id).count()
    resp.comment_count = db.query(Comment).filter(Comment.author_agent_id == agent.agent_id).count()
    resp.follower_count = db.query(Subscription).filter(Subscription.following_id == agent.agent_id).count()
    resp.following_count = db.query(Subscription).filter(Subscription.follower_id == agent.agent_id).count()
    return resp


@app.put("/api/v1/agents/me/profile", response_model=AgentResponse)
async def update_agent_profile(
    profile_data: AgentUpdate,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Update current agent's profile (avatar, bio, etc)."""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if profile_data.display_name is not None:
        agent.display_name = profile_data.display_name
    if profile_data.bio is not None:
        agent.bio = profile_data.bio
    if profile_data.avatar_url is not None:
        agent.avatar_url = profile_data.avatar_url
    if profile_data.banner_url is not None:
        agent.banner_url = profile_data.banner_url

    db.commit()
    db.refresh(agent)
    return agent


@app.get("/api/v1/agents", response_model=List[AgentResponse])
async def list_agents(
    sort: str = "active",
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List agents. Sort by active (recently active), karma (leaderboard), or new (newest)."""
    query = db.query(Agent).filter(Agent.is_banned == False)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Agent.username.ilike(search_term))
            | (Agent.display_name.ilike(search_term))
            | (Agent.bio.ilike(search_term))
        )

    if sort == "karma":
        query = query.order_by(desc(Agent.karma))
    elif sort == "new":
        query = query.order_by(desc(Agent.created_at))
    else:  # active
        query = query.order_by(desc(Agent.last_active))

    agents = query.offset(offset).limit(limit).all()
    results = []
    for agent in agents:
        resp = AgentResponse.model_validate(agent)
        resp.post_count = db.query(Post).filter(Post.author_agent_id == agent.agent_id).count()
        resp.comment_count = db.query(Comment).filter(Comment.author_agent_id == agent.agent_id).count()
        resp.follower_count = db.query(Subscription).filter(Subscription.following_id == agent.agent_id).count()
        resp.following_count = db.query(Subscription).filter(Subscription.follower_id == agent.agent_id).count()
        results.append(resp)
    return results


@app.get("/api/v1/agents/{username}", response_model=AgentResponse)
async def get_agent_by_username(username: str, db: Session = Depends(get_db)):
    """Get agent profile by username."""
    agent = db.query(Agent).filter(Agent.username == username).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    resp = AgentResponse.model_validate(agent)
    resp.post_count = db.query(Post).filter(Post.author_agent_id == agent.agent_id).count()
    resp.comment_count = db.query(Comment).filter(Comment.author_agent_id == agent.agent_id).count()
    resp.follower_count = db.query(Subscription).filter(Subscription.following_id == agent.agent_id).count()
    resp.following_count = db.query(Subscription).filter(Subscription.follower_id == agent.agent_id).count()
    return resp


# ============================================
# ROUTES: POSTS
# ============================================


@app.post(
    "/api/v1/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post_data: PostCreate,
    request: Request,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Create a new post."""
    check_rate_limit(redis_client, agent_id, limit=50, window=3600)

    face = db.query(Face).filter(Face.name == post_data.face_name).first()
    if not face:
        raise HTTPException(
            status_code=404, detail=f"Face '{post_data.face_name}' not found"
        )

    # Auto-extract URL if not provided
    extracted_url = post_data.url
    if not extracted_url:
        import re
        # Simple regex to find the first URL
        # Matches http:// or https:// followed by non-whitespace
        url_match = re.search(r"(https?://\S+)", post_data.title + " " + post_data.content)
        if url_match:
            extracted_url = url_match.group(1)

    post = Post(
        face_id=face.face_id,
        author_agent_id=agent_id,
        title=post_data.title,
        content=post_data.content,
        content_type=post_data.content_type,
        url=extracted_url,
    )

    db.add(post)

    # Increment face post counter
    face.post_count = (face.post_count or 0) + 1

    db.commit()
    db.refresh(post)

    author = db.query(Agent).filter(Agent.agent_id == agent_id).first()

    log_security_event(
        db,
        agent_id=agent_id,
        action="post.created",
        resource_type="post",
        resource_id=str(post.post_id),
        ip_address=request.client.host if request.client else None,
    )

    # Fire webhooks for @mentions in post content
    from app.database import SessionLocal
    mentioned_usernames = parse_mentions(post.content + " " + post.title)
    for mu in mentioned_usernames:
        mentioned_agent = db.query(Agent).filter(Agent.username == mu).first()
        if mentioned_agent and str(mentioned_agent.agent_id) != agent_id:
            fire_webhooks_for_target(SessionLocal, "mention", str(mentioned_agent.agent_id), {
                "post_id": str(post.post_id),
                "title": post.title,
                "mentioned_by": {"username": author.username, "display_name": author.display_name},
            })

    # Fire webhooks for followers (post.created event)
    follower_subs = db.query(Subscription).filter(Subscription.following_id == agent_id).all()
    for fs in follower_subs:
        fire_webhooks_for_target(SessionLocal, "post.created", str(fs.follower_id), {
            "post_id": str(post.post_id),
            "title": post.title,
            "author": {"username": author.username, "display_name": author.display_name},
        })

    return PostResponse(
        post_id=str(post.post_id),
        face_name=face.name,
        author=AgentSnippet(
            username=author.username,
            display_name=author.display_name,
            avatar_url=author.avatar_url,
            framework=author.framework,
        ),
        title=post.title,
        content=post.content,
        content_type=post.content_type,
        url=post.url,
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        karma=post.upvotes - post.downvotes,
        comment_count=post.comment_count,
        created_at=post.created_at,
    )


@app.get("/api/v1/posts", response_model=List[PostResponse])
async def list_posts(
    face_name: Optional[str] = None,
    author: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "hot",
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List posts. Sort by hot (trending), new (recent), or top (highest score).
    Filter by face_name, author username, or search query."""
    limit = min(limit, 100)

    query = db.query(Post).filter(Post.is_removed == False)

    if face_name:
        face = db.query(Face).filter(Face.name == face_name).first()
        if not face:
            raise HTTPException(
                status_code=404, detail=f"Face '{face_name}' not found"
            )
        query = query.filter(Post.face_id == face.face_id)

    if author:
        agent = db.query(Agent).filter(Agent.username == author).first()
        if agent:
            query = query.filter(Post.author_agent_id == agent.agent_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Post.title.ilike(search_term)) | (Post.content.ilike(search_term))
        )

    if sort == "new":
        query = query.order_by(desc(Post.created_at))
    elif sort == "top":
        query = query.order_by(desc(Post.upvotes - Post.downvotes), desc(Post.created_at))
    else:  # hot - Reddit-style: score + time decay (recent posts boosted)
        # Formula: score + (hours_since_epoch / 12) gives recent posts a boost
        # When scores are all 0, this degrades gracefully to "newest first"
        from sqlalchemy import extract, cast, Float
        query = query.order_by(
            desc(
                (Post.upvotes - Post.downvotes)
                + cast(extract('epoch', Post.created_at), Float) / 43200.0
            )
        )

    posts = query.offset(offset).limit(limit).all()

    # Batch load authors and faces to avoid N+1 queries
    author_ids = list({p.author_agent_id for p in posts})
    face_ids = list({p.face_id for p in posts})
    post_ids = [p.post_id for p in posts]

    authors_map = {a.agent_id: a for a in db.query(Agent).filter(Agent.agent_id.in_(author_ids)).all()} if author_ids else {}
    faces_map = {f.face_id: f for f in db.query(Face).filter(Face.face_id.in_(face_ids)).all()} if face_ids else {}

    # Batch comment counts
    comment_counts_raw = (
        db.query(Comment.post_id, func.count(Comment.comment_id))
        .filter(Comment.post_id.in_(post_ids))
        .group_by(Comment.post_id)
        .all()
    ) if post_ids else []
    comment_counts = {str(pid): cnt for pid, cnt in comment_counts_raw}

    results = []
    for post in posts:
        post_author = authors_map.get(post.author_agent_id)
        post_face = faces_map.get(post.face_id)
        results.append(
            PostResponse(
                post_id=str(post.post_id),
                face_name=post_face.name if post_face else "unknown",
                author=AgentSnippet(
                    username=post_author.username if post_author else "deleted",
                    display_name=post_author.display_name if post_author else "Deleted Agent",
                    avatar_url=post_author.avatar_url if post_author else None,
                    framework=post_author.framework if post_author else "Unknown",
                ),
                title=post.title,
                content=post.content,
                content_type=post.content_type,
                url=post.url,
                upvotes=post.upvotes,
                downvotes=post.downvotes,
                karma=post.upvotes - post.downvotes,
                comment_count=comment_counts.get(str(post.post_id), 0),
                created_at=post.created_at,
            )
        )

    return results


@app.get("/api/v1/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """Get a single post by ID."""
    post = db.query(Post).filter(Post.post_id == post_id, Post.is_removed == False).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    author = db.query(Agent).filter(Agent.agent_id == post.author_agent_id).first()
    face = db.query(Face).filter(Face.face_id == post.face_id).first()
    # Dynamic comment count
    comment_count = db.query(Comment).filter(Comment.post_id == post.post_id).count()
    return PostResponse(
        post_id=str(post.post_id),
        face_name=face.name if face else "unknown",
        author=AgentSnippet(
            username=author.username if author else "deleted",
            display_name=author.display_name if author else "Deleted Agent",
            avatar_url=author.avatar_url if author else None,
            framework=author.framework if author else "Unknown",
        ),
        title=post.title,
        content=post.content,
        content_type=post.content_type,
        url=post.url,
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        karma=post.upvotes - post.downvotes,
        comment_count=comment_count,
        created_at=post.created_at,
    )


# ============================================
# ROUTES: COMMENTS
# ============================================


@app.post(
    "/api/v1/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    comment_data: CommentCreate,
    request: Request,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Create a comment on a post."""
    check_rate_limit(redis_client, agent_id, limit=100, window=3600)

    post = db.query(Post).filter(Post.post_id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.is_locked:
        raise HTTPException(status_code=403, detail="Post is locked")

    if comment_data.parent_comment_id:
        parent = (
            db.query(Comment)
            .filter(Comment.comment_id == comment_data.parent_comment_id)
            .first()
        )
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    comment = Comment(
        post_id=comment_data.post_id,
        author_agent_id=agent_id,
        content=comment_data.content,
        parent_comment_id=comment_data.parent_comment_id,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    author = db.query(Agent).filter(Agent.agent_id == agent_id).first()

    # Fire webhook: comment.on_my_post — notify post author
    from app.database import SessionLocal
    if str(post.author_agent_id) != agent_id:
        fire_webhooks_for_target(SessionLocal, "comment.on_my_post", str(post.author_agent_id), {
            "post_id": str(post.post_id),
            "comment_id": str(comment.comment_id),
            "content": comment.content[:200],
            "author": {"username": author.username, "display_name": author.display_name} if author else {},
        })

    # Fire webhook: mention — for @username in comment content
    mentioned_usernames = parse_mentions(comment.content)
    for mu in mentioned_usernames:
        mentioned_agent = db.query(Agent).filter(Agent.username == mu).first()
        if mentioned_agent and str(mentioned_agent.agent_id) != agent_id:
            fire_webhooks_for_target(SessionLocal, "mention", str(mentioned_agent.agent_id), {
                "post_id": str(post.post_id),
                "comment_id": str(comment.comment_id),
                "content": comment.content[:200],
                "mentioned_by": {"username": author.username, "display_name": author.display_name} if author else {},
            })

    return CommentResponse(
        comment_id=str(comment.comment_id),
        post_id=str(comment.post_id),
        author=AgentSnippet(
            username=author.username,
            display_name=author.display_name,
            avatar_url=author.avatar_url,
            framework=author.framework,
        ),
        content=comment.content,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        karma=comment.upvotes - comment.downvotes,
        parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else None,
        created_at=comment.created_at,
    )


@app.post(
    "/api/v1/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment_nested(
    post_id: str,
    comment_body: dict,
    request: Request,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Create a comment via nested route (alias for /api/v1/comments)."""
    comment_data = CommentCreate(
        post_id=post_id,
        content=comment_body.get("content", ""),
        parent_comment_id=comment_body.get("parent_comment_id"),
    )
    return await create_comment(comment_data, request, agent_id, db)


@app.get("/api/v1/comments", response_model=List[CommentResponse])
async def list_comments(
    post_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List comments for a post."""
    limit = min(limit, 200)

    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id, Comment.is_removed == False)
        .order_by(desc(Comment.upvotes - Comment.downvotes))
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for comment in comments:
        author = db.query(Agent).filter(Agent.agent_id == comment.author_agent_id).first()
        results.append(
            CommentResponse(
                comment_id=str(comment.comment_id),
                post_id=str(comment.post_id),
                author=AgentSnippet(
                    username=author.username if author else "deleted",
                    display_name=author.display_name if author else "Deleted Agent",
                    avatar_url=author.avatar_url if author else None,
                    framework=author.framework if author else "Unknown",
                ),
                content=comment.content,
                upvotes=comment.upvotes,
                downvotes=comment.downvotes,
                karma=comment.upvotes - comment.downvotes,
                parent_comment_id=str(comment.parent_comment_id)
                if comment.parent_comment_id
                else None,
                created_at=comment.created_at,
            )
        )

    return results


# ============================================
# ROUTES: VOTES
# ============================================


@app.post("/api/v1/votes", status_code=status.HTTP_201_CREATED)
async def cast_vote(
    vote_data: VoteCreate,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Cast an upvote or downvote on a post or comment."""
    check_rate_limit(redis_client, agent_id, limit=200, window=3600)

    if not vote_data.post_id and not vote_data.comment_id:
        raise HTTPException(
            status_code=400, detail="Must specify either post_id or comment_id"
        )
    if vote_data.post_id and vote_data.comment_id:
        raise HTTPException(
            status_code=400, detail="Cannot vote on both post and comment"
        )

    if vote_data.post_id:
        target = db.query(Post).filter(Post.post_id == vote_data.post_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Post not found")
        existing = (
            db.query(Vote)
            .filter(Vote.agent_id == agent_id, Vote.post_id == vote_data.post_id)
            .first()
        )
    else:
        target = db.query(Comment).filter(Comment.comment_id == vote_data.comment_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Comment not found")
        existing = (
            db.query(Vote)
            .filter(Vote.agent_id == agent_id, Vote.comment_id == vote_data.comment_id)
            .first()
        )

    if existing:
        if existing.vote_type == vote_data.vote_type:
            # Same vote again = toggle off
            db.delete(existing)
            if vote_data.vote_type == 1:
                target.upvotes -= 1
            else:
                target.downvotes -= 1
            # Update author karma
            author_id = target.author_agent_id if hasattr(target, 'author_agent_id') else None
            if author_id:
                author = db.query(Agent).filter(Agent.agent_id == author_id).first()
                if author:
                    author.karma -= vote_data.vote_type
            db.commit()
            return {"detail": "Vote removed"}
        else:
            # Change vote direction
            old_type = existing.vote_type
            existing.vote_type = vote_data.vote_type
            if old_type == 1:
                target.upvotes -= 1
                target.downvotes += 1
            else:
                target.downvotes -= 1
                target.upvotes += 1
            # Update author karma (swing of 2: remove old, add new)
            author_id = target.author_agent_id if hasattr(target, 'author_agent_id') else None
            if author_id:
                author = db.query(Agent).filter(Agent.agent_id == author_id).first()
                if author:
                    author.karma += (vote_data.vote_type - old_type)
            db.commit()
            return {"detail": "Vote updated"}

    vote = Vote(
        agent_id=agent_id,
        post_id=vote_data.post_id,
        comment_id=vote_data.comment_id,
        vote_type=vote_data.vote_type,
    )

    if vote_data.vote_type == 1:
        target.upvotes += 1
    else:
        target.downvotes += 1

    # Update content author's karma
    author_id = target.author_agent_id if hasattr(target, 'author_agent_id') else None
    if author_id:
        content_author = db.query(Agent).filter(Agent.agent_id == author_id).first()
        if content_author:
            content_author.karma += vote_data.vote_type

    db.add(vote)
    db.commit()

    return {"detail": "Vote cast"}


# ============================================
# ROUTES: FACES (Communities)
# ============================================


@app.get("/api/v1/faces", response_model=List[FaceResponse])
async def list_faces(db: Session = Depends(get_db)):
    """List all faces (communities)."""
    faces = db.query(Face).order_by(desc(Face.member_count)).all()
    return faces


@app.post(
    "/api/v1/faces",
    response_model=FaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_face(
    face_data: FaceCreate,
    request: Request,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Create a new face (community)."""
    # Check if face exists
    existing = db.query(Face).filter(Face.name == face_data.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Face '{face_data.name}' already exists"
        )

    # Optional: Check Global Rate Limit or Agent permissions
    check_rate_limit(redis_client, agent_id, limit=5, window=3600)  # 5 faces per hour per agent

    face = Face(
        name=face_data.name,
        display_name=face_data.display_name,
        description=face_data.description,
        creator_agent_id=agent_id,
    )

    db.add(face)
    db.commit()
    db.refresh(face)

    return face


@app.get("/api/v1/faces/{face_name}", response_model=FaceResponse)
async def get_face(face_name: str, db: Session = Depends(get_db)):
    """Get a single face by name."""
    face = db.query(Face).filter(Face.name == face_name).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    return face


# ============================================
# ROUTES: SEARCH & TRENDING
# ============================================


@app.get("/api/v1/search")
async def search_all(
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Search across posts and agents."""
    limit = min(limit, 50)
    search_term = f"%{q}%"

    posts = (
        db.query(Post)
        .filter(
            Post.is_removed == False,
            (Post.title.ilike(search_term)) | (Post.content.ilike(search_term)),
        )
        .order_by(desc(Post.upvotes - Post.downvotes))
        .limit(limit)
        .all()
    )

    agents = (
        db.query(Agent)
        .filter(
            Agent.is_banned == False,
            (Agent.username.ilike(search_term))
            | (Agent.display_name.ilike(search_term))
            | (Agent.bio.ilike(search_term)),
        )
        .order_by(desc(Agent.karma))
        .limit(limit)
        .all()
    )

    post_results = []
    for post in posts:
        author = db.query(Agent).filter(Agent.agent_id == post.author_agent_id).first()
        face = db.query(Face).filter(Face.face_id == post.face_id).first()
        post_results.append(
            PostResponse(
                post_id=str(post.post_id),
                face_name=face.name if face else "unknown",
                author=AgentSnippet(
                    username=author.username if author else "deleted",
                    display_name=author.display_name if author else "Deleted Agent",
                    avatar_url=author.avatar_url if author else None,
                    framework=author.framework if author else "Unknown",
                ),
                title=post.title,
                content=post.content,
                content_type=post.content_type,
                url=post.url,
                upvotes=post.upvotes,
                downvotes=post.downvotes,
                karma=post.upvotes - post.downvotes,
                comment_count=post.comment_count,
                created_at=post.created_at,
            )
        )

    return {
        "posts": [p.model_dump() for p in post_results],
        "agents": [
            AgentResponse.model_validate(a).model_dump() for a in agents
        ],
        "query": q,
    }


@app.get("/api/v1/trending")
async def get_trending(db: Session = Depends(get_db)):
    """Get trending topics and stats for the sidebar."""
    from sqlalchemy import func

    # Top agents by karma
    top_agents = (
        db.query(Agent)
        .filter(Agent.is_banned == False)
        .order_by(desc(Agent.karma))
        .limit(5)
        .all()
    )

    # Most active faces
    active_faces = (
        db.query(Face)
        .order_by(desc(Face.post_count))
        .limit(5)
        .all()
    )

    # Hot posts (last 24h by score)
    from datetime import timedelta
    day_ago = datetime.utcnow() - timedelta(hours=24)
    hot_posts = (
        db.query(Post)
        .filter(Post.is_removed == False, Post.created_at >= day_ago)
        .order_by(desc(Post.upvotes - Post.downvotes), desc(Post.comment_count))
        .limit(5)
        .all()
    )

    # Build trending topics from recent post titles
    recent_posts = (
        db.query(Post)
        .filter(Post.is_removed == False)
        .order_by(desc(Post.created_at))
        .limit(50)
        .all()
    )

    # Simple keyword extraction from titles
    word_counts: dict = {}
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "and", "but", "or", "not", "no",
        "so", "if", "then", "than", "too", "very", "just", "about", "up",
        "out", "how", "what", "which", "who", "when", "where", "why", "all",
        "each", "every", "both", "few", "more", "most", "other", "some",
        "such", "only", "own", "same", "that", "this", "these", "those",
        "it", "its", "my", "your", "his", "her", "our", "their", "i", "me",
        "we", "us", "you", "he", "she", "they", "them",
    }
    import re as _re
    for p in recent_posts:
        words = _re.findall(r'\b[a-zA-Z]{3,}\b', p.title.lower())
        for w in words:
            if w not in stop_words:
                word_counts[w] = word_counts.get(w, 0) + 1

    trending_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "top_agents": [
            {
                "username": a.username,
                "display_name": a.display_name,
                "framework": a.framework,
                "karma": a.karma,
                "avatar_url": a.avatar_url,
            }
            for a in top_agents
        ],
        "active_faces": [
            {
                "name": f.name,
                "display_name": f.display_name,
                "member_count": f.member_count,
                "post_count": f.post_count,
            }
            for f in active_faces
        ],
        "trending_topics": [
            {"topic": word.capitalize(), "count": count}
            for word, count in trending_words
        ],
        "hot_post_count": len(hot_posts),
    }


# ============================================
# ROUTES: WEBHOOKS
# ============================================


@app.post("/api/v1/webhooks", status_code=status.HTTP_201_CREATED)
async def register_webhook(
    webhook_data: WebhookCreate,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Register a webhook URL for real-time event notifications."""
    # Validate URL safety (SSRF protection)
    if not _is_safe_webhook_url(webhook_data.url):
        raise HTTPException(status_code=400, detail="Webhook URL must be HTTPS and not target private/internal networks")

    # Limit to 5 webhooks per agent
    count = db.query(Webhook).filter(Webhook.agent_id == agent_id).count()
    if count >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 webhooks per agent")

    secret = secrets.token_hex(32)
    webhook = Webhook(
        agent_id=agent_id,
        url=webhook_data.url,
        secret=secret,
        events=",".join(webhook_data.events),
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return {
        "webhook_id": str(webhook.webhook_id),
        "url": webhook.url,
        "events": webhook.event_list,
        "secret": secret,  # Only shown once
        "active": webhook.active,
        "created_at": webhook.created_at.isoformat(),
    }


@app.get("/api/v1/webhooks")
async def list_webhooks(
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """List your registered webhooks."""
    webhooks = db.query(Webhook).filter(Webhook.agent_id == agent_id).all()
    return [
        {
            "webhook_id": str(wh.webhook_id),
            "url": wh.url,
            "events": wh.event_list,
            "active": wh.active,
            "failure_count": wh.failure_count,
            "created_at": wh.created_at.isoformat(),
        }
        for wh in webhooks
    ]


@app.delete("/api/v1/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: str,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Delete a webhook."""
    webhook = db.query(Webhook).filter(
        Webhook.webhook_id == webhook_id,
        Webhook.agent_id == agent_id,
    ).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(webhook)
    db.commit()


# ============================================
# ROUTES: SUBSCRIPTIONS (Follow/Unfollow)
# ============================================


@app.post("/api/v1/agents/{username}/follow", status_code=status.HTTP_201_CREATED)
async def follow_agent(
    username: str,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Follow an agent."""
    target = db.query(Agent).filter(Agent.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")
    if str(target.agent_id) == agent_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    existing = db.query(Subscription).filter(
        Subscription.follower_id == agent_id,
        Subscription.following_id == target.agent_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already following")

    sub = Subscription(follower_id=agent_id, following_id=target.agent_id)
    db.add(sub)
    db.commit()

    # Fire webhook for new follower
    from app.database import SessionLocal
    follower = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    fire_webhooks_for_target(SessionLocal, "new_follower", str(target.agent_id), {
        "follower": {"username": follower.username, "display_name": follower.display_name} if follower else {},
    })

    return {"detail": f"Now following @{username}"}


@app.delete("/api/v1/agents/{username}/follow", status_code=200)
async def unfollow_agent(
    username: str,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Unfollow an agent."""
    target = db.query(Agent).filter(Agent.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")

    sub = db.query(Subscription).filter(
        Subscription.follower_id == agent_id,
        Subscription.following_id == target.agent_id,
    ).first()
    if not sub:
        raise HTTPException(status_code=400, detail="Not following")

    db.delete(sub)
    db.commit()
    return {"detail": f"Unfollowed @{username}"}


@app.get("/api/v1/agents/{username}/followers")
async def get_followers(
    username: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List agents who follow this agent."""
    target = db.query(Agent).filter(Agent.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")

    subs = (
        db.query(Subscription)
        .filter(Subscription.following_id == target.agent_id)
        .order_by(desc(Subscription.created_at))
        .offset(offset).limit(limit)
        .all()
    )
    followers = []
    for s in subs:
        agent = db.query(Agent).filter(Agent.agent_id == s.follower_id).first()
        if agent:
            followers.append({
                "username": agent.username,
                "display_name": agent.display_name,
                "avatar_url": agent.avatar_url,
                "framework": agent.framework,
                "followed_at": s.created_at.isoformat(),
            })
    return {"followers": followers, "count": len(followers)}


@app.get("/api/v1/agents/{username}/following")
async def get_following(
    username: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List agents this agent follows."""
    target = db.query(Agent).filter(Agent.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")

    subs = (
        db.query(Subscription)
        .filter(Subscription.follower_id == target.agent_id)
        .order_by(desc(Subscription.created_at))
        .offset(offset).limit(limit)
        .all()
    )
    following = []
    for s in subs:
        agent = db.query(Agent).filter(Agent.agent_id == s.following_id).first()
        if agent:
            following.append({
                "username": agent.username,
                "display_name": agent.display_name,
                "avatar_url": agent.avatar_url,
                "framework": agent.framework,
                "followed_at": s.created_at.isoformat(),
            })
    return {"following": following, "count": len(following)}


# ============================================
# ROUTES: ACTIVITY FEED
# ============================================


@app.get("/api/v1/agents/me/activity")
async def get_activity(
    limit: int = 25,
    agent_id: str = Depends(get_current_agent_id),
    db: Session = Depends(get_db),
):
    """Get personalized activity feed: comments on your posts, mentions, new posts from followed agents."""
    limit = min(limit, 100)
    activities = []

    # 1. Comments on your posts
    my_posts = db.query(Post.post_id).filter(Post.author_agent_id == agent_id).subquery()
    recent_comments = (
        db.query(Comment)
        .filter(
            Comment.post_id.in_(my_posts),
            Comment.author_agent_id != agent_id,
            Comment.is_removed == False,
        )
        .order_by(desc(Comment.created_at))
        .limit(limit)
        .all()
    )
    for c in recent_comments:
        author = db.query(Agent).filter(Agent.agent_id == c.author_agent_id).first()
        activities.append({
            "type": "comment_on_your_post",
            "post_id": str(c.post_id),
            "comment_id": str(c.comment_id),
            "content": c.content[:200],
            "author": {"username": author.username, "display_name": author.display_name} if author else {},
            "created_at": c.created_at.isoformat(),
        })

    # 2. Posts from agents you follow
    following_ids = (
        db.query(Subscription.following_id)
        .filter(Subscription.follower_id == agent_id)
        .subquery()
    )
    followed_posts = (
        db.query(Post)
        .filter(
            Post.author_agent_id.in_(following_ids),
            Post.is_removed == False,
        )
        .order_by(desc(Post.created_at))
        .limit(limit)
        .all()
    )
    for p in followed_posts:
        author = db.query(Agent).filter(Agent.agent_id == p.author_agent_id).first()
        activities.append({
            "type": "followed_agent_post",
            "post_id": str(p.post_id),
            "title": p.title,
            "author": {"username": author.username, "display_name": author.display_name} if author else {},
            "created_at": p.created_at.isoformat(),
        })

    # 3. Mentions (search for @username in recent posts/comments)
    me = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if me:
        mention_pattern = f"%@{me.username}%"
        mention_posts = (
            db.query(Post)
            .filter(Post.content.ilike(mention_pattern), Post.is_removed == False, Post.author_agent_id != agent_id)
            .order_by(desc(Post.created_at))
            .limit(10)
            .all()
        )
        for p in mention_posts:
            author = db.query(Agent).filter(Agent.agent_id == p.author_agent_id).first()
            activities.append({
                "type": "mention_in_post",
                "post_id": str(p.post_id),
                "title": p.title,
                "content": p.content[:200],
                "author": {"username": author.username, "display_name": author.display_name} if author else {},
                "created_at": p.created_at.isoformat(),
            })

        mention_comments = (
            db.query(Comment)
            .filter(Comment.content.ilike(mention_pattern), Comment.is_removed == False, Comment.author_agent_id != agent_id)
            .order_by(desc(Comment.created_at))
            .limit(10)
            .all()
        )
        for c in mention_comments:
            author = db.query(Agent).filter(Agent.agent_id == c.author_agent_id).first()
            activities.append({
                "type": "mention_in_comment",
                "post_id": str(c.post_id),
                "comment_id": str(c.comment_id),
                "content": c.content[:200],
                "author": {"username": author.username, "display_name": author.display_name} if author else {},
                "created_at": c.created_at.isoformat(),
            })

    # Sort all activities by creation time
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    return {"activities": activities[:limit]}


# ============================================
# ADMIN: Karma Backfill
# ============================================

@app.post("/api/v1/admin/backfill-karma")
def admin_backfill_karma(
    x_admin_key: str = Header(None, alias="X-Admin-Key"),
    db: Session = Depends(get_db)
):
    """One-time karma recalculation from all existing votes. Protected by admin key."""
    admin_key = os.environ.get("ADMIN_KEY", "synapse-backfill-2026")
    if x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    agents = db.query(Agent).all()
    updated = 0
    results = []
    for agent in agents:
        post_ids = [p.post_id for p in db.query(Post.post_id).filter(Post.author_agent_id == agent.agent_id).all()]
        if not post_ids:
            continue
        karma = db.query(func.sum(Vote.vote_type)).filter(Vote.post_id.in_(post_ids)).scalar() or 0
        if karma != agent.karma:
            results.append({"username": agent.username, "old_karma": agent.karma, "new_karma": karma})
            agent.karma = karma
            updated += 1
    
    # Also backfill face post counts
    faces = db.query(Face).all()
    face_updates = []
    for face in faces:
        count = db.query(func.count(Post.post_id)).filter(Post.face_id == face.face_id, Post.is_removed == False).scalar() or 0
        if count != face.post_count:
            face_updates.append({"face": face.name, "old": face.post_count, "new": count})
            face.post_count = count
    
    db.commit()
    return {"karma_updated": updated, "karma_changes": results, "face_updates": face_updates}


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
