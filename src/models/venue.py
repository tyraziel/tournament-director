"""Venue data model.

AIA PAI Hin R Claude Code v1.0
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Venue(BaseModel):
    """Tournament venue definition."""

    id: UUID
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
