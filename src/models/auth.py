"""
Authentication models for API token management.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class APIKey(BaseModel):
    """
    API authentication token for securing API access.

    Each API key belongs to a player and can be used to authenticate
    API requests via Bearer token authentication.
    """

    id: UUID = Field(default_factory=uuid4)
    token: str = Field(..., min_length=32, max_length=256)
    name: str = Field(..., min_length=1, max_length=100)
    created_by: UUID  # Player ID who owns this token
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    permissions: Optional[Dict[str, bool]] = None  # Future: RBAC scopes

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )
