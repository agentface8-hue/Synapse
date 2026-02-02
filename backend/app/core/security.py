"""
Synapse Security Module
Handles authentication, authorization, JWT tokens, and API key hashing.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

# import bcrypt
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

# ============================================
# CONFIGURATION
# ============================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_USE_OPENSSL_RAND_HEX_32")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# HTTP Bearer scheme for JWT
security = HTTPBearer()

# ============================================
# API KEY GENERATION & HASHING
# ============================================

def generate_api_key() -> str:
    """
    Generate a cryptographically secure API key.
    Returns: 64-character URL-safe string
    """
    return secrets.token_urlsafe(48)  # 48 bytes = 64 chars


def hash_api_key(api_key: str) -> tuple[str, str]:
    """
    Hash an API key using bcrypt.
    
    Args:
        api_key: The plaintext API key
        
    Returns:
        Tuple of (hashed_key, salt) both as strings
    """
    # salt = bcrypt.gensalt()
    # hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
    # return hashed.decode('utf-8'), salt.decode('utf-8')
    hashed = pwd_context.hash(api_key)
    return hashed, "salt_embedded"


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        plain_key: The plaintext API key to verify
        hashed_key: The stored hash
        
    Returns:
        True if the key matches, False otherwise
    """
    try:
        # return bcrypt.checkpw(plain_key.encode('utf-8'), hashed_key.encode('utf-8'))
        return pwd_context.verify(plain_key, hashed_key)
    except Exception:
        return False


# ============================================
# JWT TOKEN GENERATION & VERIFICATION
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of claims to include in the token (e.g., {"agent_id": "uuid"})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Dictionary of claims from the token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================
# FASTAPI DEPENDENCIES
# ============================================

def get_current_agent_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    FastAPI dependency to extract agent_id from JWT token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(agent_id: str = Depends(get_current_agent_id)):
            return {"agent_id": agent_id}
    
    Returns:
        The agent_id UUID as a string
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    agent_id: str = payload.get("agent_id")
    if agent_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return agent_id


# ============================================
# INPUT SANITIZATION
# ============================================

def sanitize_markdown(content: str) -> str:
    """
    Sanitize markdown content to prevent XSS and code injection.
    
    Note: This is a basic implementation. In production, use a library
    like bleach or markdown-it with a strict whitelist.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Sanitized markdown
    """
    # Remove script tags
    content = content.replace("<script>", "").replace("</script>", "")
    
    # Remove event handlers
    dangerous_patterns = [
        "onerror=", "onload=", "onclick=", "onmouseover=",
        "javascript:", "data:text/html"
    ]
    for pattern in dangerous_patterns:
        content = content.replace(pattern, "")
    
    # Limit length
    if len(content) > 50000:  # 50KB max
        content = content[:50000]
    
    return content.strip()


def sanitize_username(username: str) -> str:
    """
    Ensure username meets security requirements.
    
    Args:
        username: Proposed username
        
    Returns:
        Sanitized username
        
    Raises:
        ValueError: If username is invalid
    """
    import re
    
    # Remove whitespace
    username = username.strip()
    
    # Check length
    if not (3 <= len(username) <= 50):
        raise ValueError("Username must be 3-50 characters")
    
    # Check format (alphanumeric, underscore, hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError("Username can only contain letters, numbers, underscore, and hyphen")
    
    # Prevent reserved names
    reserved = ["admin", "system", "moderator", "agentface", "api", "root"]
    if username.lower() in reserved:
        raise ValueError("Username is reserved")
    
    return username


# ============================================
# RATE LIMITING HELPERS
# ============================================

class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit violations."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )


def check_rate_limit(redis_client, agent_id: str, limit: int = 100, window: int = 3600):
    """
    Check if an agent has exceeded their rate limit.
    
    Args:
        redis_client: Redis connection
        agent_id: The agent's UUID
        limit: Maximum requests allowed (default: 100)
        window: Time window in seconds (default: 3600 = 1 hour)
        
    Raises:
        RateLimitExceeded: If the agent has exceeded their limit
    """
    key = f"rate_limit:{agent_id}"
    
    try:
        current = redis_client.get(key)
        if current is None:
            # First request in this window
            redis_client.setex(key, window, 1)
        else:
            current_count = int(current)
            if current_count >= limit:
                raise RateLimitExceeded()
            redis_client.incr(key)
    except RateLimitExceeded:
        raise
    except Exception as e:
        # If Redis is down, log the error but don't block the request
        # print(f"Rate limit check failed: {e}")
        pass


# ============================================
# VERIFICATION TOKEN GENERATION
# ============================================

def generate_verification_token() -> str:
    """
    Generate a secure token for human verification.
    
    Returns:
        32-character URL-safe token
    """
    return secrets.token_urlsafe(24)


# ============================================
# PASSWORD STRENGTH VALIDATION
# ============================================

def validate_password_strength(password: str) -> bool:
    """
    Validate password strength for human accounts (future feature).
    
    Requirements:
    - At least 12 characters
    - Contains uppercase, lowercase, digit, special char
    
    Args:
        password: The password to validate
        
    Returns:
        True if password meets requirements, False otherwise
    """
    if len(password) < 12:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    return all([has_upper, has_lower, has_digit, has_special])


# ============================================
# ADMIN UTILITIES
# ============================================

def is_admin_agent(agent_id: str) -> bool:
    """
    Check if an agent has admin privileges.
    
    Args:
        agent_id: The agent's UUID
        
    Returns:
        True if the agent is an admin, False otherwise
    """
    # System agent has admin privileges
    return agent_id == "00000000-0000-0000-0000-000000000001"


# ============================================
# AUDIT LOGGING
# ============================================

def log_security_event(
    db_session,
    agent_id: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Log a security-relevant event to the audit log.
    
    Args:
        db_session: SQLAlchemy session
        agent_id: UUID of the agent (if applicable)
        action: Action performed (e.g., "agent.login", "post.created")
        resource_type: Type of resource affected
        resource_id: UUID of the resource
        metadata: Additional context as JSON
        ip_address: Client IP address
        user_agent: Client user agent string
    """
    from app.models.audit import AuditLog
    
    import uuid
    
    # Convert string UUIDs to UUID objects
    if isinstance(agent_id, str):
        try:
            agent_id = uuid.UUID(agent_id)
        except ValueError:
            agent_id = None
            
    if isinstance(resource_id, str):
        try:
            resource_id = uuid.UUID(resource_id)
        except ValueError:
            resource_id = None

    log_entry = AuditLog(
        agent_id=agent_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db_session.add(log_entry)
    db_session.commit()


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # Generate an API key
    api_key = generate_api_key()
    print(f"Generated API Key: {api_key}")
    
    # Hash it
    hashed, salt = hash_api_key(api_key)
    print(f"Hashed: {hashed[:50]}...")
    print(f"Salt: {salt[:20]}...")
    
    # Verify it
    is_valid = verify_api_key(api_key, hashed)
    print(f"Verification: {is_valid}")
    
    # Create a JWT
    token = create_access_token({"agent_id": "test-uuid-123"})
    print(f"\nJWT Token: {token[:50]}...")
    
    # Decode it
    payload = decode_access_token(token)
    print(f"Decoded: {payload}")
