"""
Token generation utilities for API authentication.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""
import secrets


def generate_api_token(length: int = 64) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Number of random bytes to generate (default: 64)
                The output will be length * 2 characters (hex encoding)

    Returns:
        Hex string token suitable for API authentication

    Example:
        >>> token = generate_api_token()
        >>> len(token)
        128
        >>> token = generate_api_token(32)
        >>> len(token)
        64
    """
    return secrets.token_hex(length)
