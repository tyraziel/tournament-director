"""Venue data model.

AIA PAI Hin R Claude Code v1.0
AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - 2025-11-19 - Added API models
"""

from uuid import UUID

from pydantic import BaseModel, Field


class Venue(BaseModel):
    """Tournament venue definition."""

    id: UUID
    name: str
    address: str | None = None
    description: str | None = None


class VenueCreate(BaseModel):
    """Venue creation request model for API."""

    name: str = Field(..., min_length=1, max_length=200)
    address: str | None = None
    description: str | None = None


class VenueUpdate(BaseModel):
    """Venue update request model for API."""

    name: str | None = Field(None, min_length=1, max_length=200)
    address: str | None = None
    description: str | None = None
