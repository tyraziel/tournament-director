"""Format data model.

AIA PAI Hin R Claude Code v1.0
"""

from uuid import UUID

from pydantic import BaseModel

from .base import BaseFormat, GameSystem


class Format(BaseModel):
    """Tournament format definition."""

    id: UUID
    name: str
    game_system: GameSystem
    base_format: BaseFormat
    sub_format: str | None = None
    card_pool: str
    match_structure: str | None = None  # "BO1", "BO3", etc.
    description: str | None = None
