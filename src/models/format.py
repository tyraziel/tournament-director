"""Format data model.

AIA PAI Hin R Claude Code v1.0
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import BaseFormat, GameSystem


class Format(BaseModel):
    """Tournament format definition."""

    id: UUID
    name: str
    game_system: GameSystem
    base_format: BaseFormat
    sub_format: Optional[str] = None
    card_pool: str
    match_structure: Optional[str] = None  # "BO1", "BO3", etc.
    description: Optional[str] = None
