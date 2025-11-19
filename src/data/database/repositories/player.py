"""Database repository for Player entities.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.exceptions import DuplicateError, NotFoundError
from src.data.interface import PlayerRepository
from src.data.database.models import PlayerModel
from src.models.player import Player


class DatabasePlayerRepository(PlayerRepository):
    """Database implementation of PlayerRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(self, player: Player) -> Player:
        """Create a new player."""
        # Check for duplicate ID
        existing = await self.session.get(PlayerModel, player.id)
        if existing:
            raise DuplicateError("Player", "id", player.id)

        # Check for duplicate discord_id
        if player.discord_id:
            stmt = select(PlayerModel).where(PlayerModel.discord_id == player.discord_id)
            result = await self.session.execute(stmt)
            if result.scalar_one_or_none():
                raise DuplicateError("Player", "discord_id", player.discord_id)

        # Create model from Pydantic
        db_player = PlayerModel(
            id=player.id,
            name=player.name,
            discord_id=player.discord_id,
            email=player.email,
            created_at=player.created_at,
        )

        self.session.add(db_player)
        await self.session.flush()  # Ensure it's persisted

        return player

    async def get_by_id(self, player_id: UUID) -> Player:
        """Get player by ID. Raises NotFoundError if not found."""
        db_player = await self.session.get(PlayerModel, player_id)
        if not db_player:
            raise NotFoundError("Player", player_id)

        return Player(
            id=db_player.id,
            name=db_player.name,
            discord_id=db_player.discord_id,
            email=db_player.email,
            created_at=db_player.created_at,
        )

    async def get_by_name(self, name: str) -> Optional[Player]:
        """Get player by name. Returns None if not found."""
        stmt = select(PlayerModel).where(PlayerModel.name == name)
        result = await self.session.execute(stmt)
        db_player = result.scalar_one_or_none()

        if not db_player:
            return None

        return Player(
            id=db_player.id,
            name=db_player.name,
            discord_id=db_player.discord_id,
            email=db_player.email,
            created_at=db_player.created_at,
        )

    async def get_by_discord_id(self, discord_id: str) -> Optional[Player]:
        """Get player by Discord ID. Returns None if not found."""
        stmt = select(PlayerModel).where(PlayerModel.discord_id == discord_id)
        result = await self.session.execute(stmt)
        db_player = result.scalar_one_or_none()

        if not db_player:
            return None

        return Player(
            id=db_player.id,
            name=db_player.name,
            discord_id=db_player.discord_id,
            email=db_player.email,
            created_at=db_player.created_at,
        )

    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Player]:
        """List all players with optional pagination."""
        stmt = select(PlayerModel).offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        db_players = result.scalars().all()

        return [
            Player(
                id=db_player.id,
                name=db_player.name,
                discord_id=db_player.discord_id,
                email=db_player.email,
                created_at=db_player.created_at,
            )
            for db_player in db_players
        ]

    async def update(self, player: Player) -> Player:
        """Update an existing player."""
        db_player = await self.session.get(PlayerModel, player.id)
        if not db_player:
            raise NotFoundError("Player", player.id)

        # Update fields
        db_player.name = player.name
        db_player.discord_id = player.discord_id
        db_player.email = player.email
        # created_at is immutable

        await self.session.flush()

        return player

    async def delete(self, player_id: UUID) -> None:
        """Delete a player. Raises NotFoundError if not found."""
        db_player = await self.session.get(PlayerModel, player_id)
        if not db_player:
            raise NotFoundError("Player", player_id)

        await self.session.delete(db_player)
        await self.session.flush()
