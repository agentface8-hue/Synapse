"""
Input sanitization utilities for AgentFace.
"""

import re
from typing import Optional


def strip_html_tags(text: str) -> str:
    """Remove all HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text)


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """Validate and sanitize a URL. Returns None if invalid."""
    if url is None:
        return None
    url = url.strip()
    if not url:
        return None
    # Only allow http and https schemes
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return None
    # Block javascript: and data: schemes that might be obfuscated
    if re.search(r"javascript:|data:", url, re.IGNORECASE):
        return None
    if len(url) > 2000:
        return None
    return url


def sanitize_display_name(name: str) -> str:
    """Sanitize a display name."""
    name = strip_html_tags(name).strip()
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name)
    if len(name) > 100:
        name = name[:100]
    return name
