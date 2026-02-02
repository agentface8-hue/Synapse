"""
Synapse SDK Exceptions
"""


class SynapseError(Exception):
    """Base exception for Synapse SDK"""
    pass


class AuthenticationError(SynapseError):
    """Raised when authentication fails"""
    pass


class RateLimitError(SynapseError):
    """Raised when rate limit is exceeded"""
    pass


class ValidationError(SynapseError):
    """Raised when input validation fails"""
    pass


class NotFoundError(SynapseError):
    """Raised when a resource is not found"""
    pass
