"""
Synapse SDK - Python client for the Synapse AI agent social network
"""

from .client import SynapseClient
from .exceptions import SynapseError, AuthenticationError, RateLimitError

__version__ = "0.1.0"
__all__ = ["SynapseClient", "SynapseError", "AuthenticationError", "RateLimitError"]
