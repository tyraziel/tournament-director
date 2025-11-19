"""Database repository for Format entities.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.exceptions import DuplicateError, NotFoundError
from src.data.interface import FormatRepository
from src.data.database.models import FormatModel
from src.models.format import Format
from src.models.base import GameSystem, BaseFormat


class DatabaseFormatRepository(FormatRepository):
    """Database implementation of FormatRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(self, format_obj: Format) -> Format:
        """Create a new format."""
        # Check for duplicate ID
        existing = await self.session.get(FormatModel, format_obj.id)
        if existing:
            raise DuplicateError(f"Format with ID {format_obj.id} already exists")

        db_format = FormatModel(
            id=format_obj.id,
            name=format_obj.name,
            game_system=format_obj.game_system.value,
            base_format=format_obj.base_format.value,
            sub_format=format_obj.sub_format,
            card_pool=format_obj.card_pool,
            match_structure=format_obj.match_structure,
            description=format_obj.description,
        )

        self.session.add(db_format)
        await self.session.flush()

        return format_obj

    async def get_by_id(self, format_id: UUID) -> Format:
        """Get format by ID. Raises NotFoundError if not found."""
        db_format = await self.session.get(FormatModel, format_id)
        if not db_format:
            raise NotFoundError(f"Format with ID {format_id} not found")

        return Format(
            id=db_format.id,
            name=db_format.name,
            game_system=GameSystem(db_format.game_system),
            base_format=BaseFormat(db_format.base_format),
            sub_format=db_format.sub_format,
            card_pool=db_format.card_pool,
            match_structure=db_format.match_structure,
            description=db_format.description,
        )

    async def get_by_name(
        self, name: str, game_system: Optional[str] = None
    ) -> Optional[Format]:
        """Get format by name and optionally game system. Returns None if not found."""
        stmt = select(FormatModel).where(FormatModel.name == name)
        if game_system:
            stmt = stmt.where(FormatModel.game_system == game_system)

        result = await self.session.execute(stmt)
        db_format = result.scalar_one_or_none()

        if not db_format:
            return None

        return Format(
            id=db_format.id,
            name=db_format.name,
            game_system=GameSystem(db_format.game_system),
            base_format=BaseFormat(db_format.base_format),
            sub_format=db_format.sub_format,
            card_pool=db_format.card_pool,
            match_structure=db_format.match_structure,
            description=db_format.description,
        )

    async def list_by_game_system(self, game_system: str) -> List[Format]:
        """List all formats for a specific game system."""
        stmt = select(FormatModel).where(FormatModel.game_system == game_system)
        result = await self.session.execute(stmt)
        db_formats = result.scalars().all()

        return [
            Format(
                id=db_format.id,
                name=db_format.name,
                game_system=GameSystem(db_format.game_system),
                base_format=BaseFormat(db_format.base_format),
                sub_format=db_format.sub_format,
                card_pool=db_format.card_pool,
                match_structure=db_format.match_structure,
                description=db_format.description,
            )
            for db_format in db_formats
        ]

    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Format]:
        """List all formats with optional pagination."""
        stmt = select(FormatModel).offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        db_formats = result.scalars().all()

        return [
            Format(
                id=db_format.id,
                name=db_format.name,
                game_system=GameSystem(db_format.game_system),
                base_format=BaseFormat(db_format.base_format),
                sub_format=db_format.sub_format,
                card_pool=db_format.card_pool,
                match_structure=db_format.match_structure,
                description=db_format.description,
            )
            for db_format in db_formats
        ]

    async def update(self, format_obj: Format) -> Format:
        """Update an existing format."""
        db_format = await self.session.get(FormatModel, format_obj.id)
        if not db_format:
            raise NotFoundError(f"Format with ID {format_obj.id} not found")

        db_format.name = format_obj.name
        db_format.game_system = format_obj.game_system.value
        db_format.base_format = format_obj.base_format.value
        db_format.sub_format = format_obj.sub_format
        db_format.card_pool = format_obj.card_pool
        db_format.match_structure = format_obj.match_structure
        db_format.description = format_obj.description

        await self.session.flush()

        return format_obj

    async def delete(self, format_id: UUID) -> None:
        """Delete a format. Raises NotFoundError if not found."""
        db_format = await self.session.get(FormatModel, format_id)
        if not db_format:
            raise NotFoundError(f"Format with ID {format_id} not found")

        await self.session.delete(db_format)
        await self.session.flush()
