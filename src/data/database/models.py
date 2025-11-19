"""SQLAlchemy database models for Tournament Director.

Maps Pydantic models to database tables for SQLite, PostgreSQL, MySQL, and MariaDB.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from datetime import datetime
from typing import Any
from uuid import UUID as PyUUID  # noqa: N811  # SQLAlchemy type alias

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.data.database.types import JSON, UUID


class Base(DeclarativeBase):
    """Base class for all database models."""



class PlayerModel(Base):
    """Player table - global player identity across all tournaments."""

    __tablename__ = "players"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    discord_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class VenueModel(Base):
    """Venue table - tournament venue definitions."""

    __tablename__ = "venues"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)


class FormatModel(Base):
    """Format table - tournament format definitions."""

    __tablename__ = "formats"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    game_system: Mapped[str] = mapped_column(String(50), nullable=False)
    base_format: Mapped[str] = mapped_column(String(50), nullable=False)
    sub_format: Mapped[str | None] = mapped_column(String(100), nullable=True)
    card_pool: Mapped[str] = mapped_column(String(200), nullable=False)
    match_structure: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)


class TournamentModel(Base):
    """Tournament table - tournament definitions and metadata."""

    __tablename__ = "tournaments"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    visibility: Mapped[str] = mapped_column(String(50), nullable=False)

    # RegistrationControl embedded as JSON
    registration: Mapped[dict[str, Any]] = mapped_column(JSON(), nullable=False)

    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Foreign keys
    format_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("formats.id"), nullable=False
    )
    venue_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("venues.id"), nullable=False
    )
    created_by: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("players.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    registration_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    auto_advance_rounds: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)


class TournamentRegistrationModel(Base):
    """Tournament registration table - player registrations for tournaments."""

    __tablename__ = "tournament_registrations"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)

    # Foreign keys
    tournament_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("tournaments.id"), nullable=False
    )
    player_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("players.id"), nullable=False
    )

    sequence_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    registration_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    drop_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)


class ComponentModel(Base):
    """Component table - tournament components (Swiss, Elimination, etc.)."""

    __tablename__ = "components"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)

    # Foreign key
    tournament_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("tournaments.id"), nullable=False
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer(), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Component-specific configuration stored as JSON
    config: Mapped[dict[str, Any]] = mapped_column(JSON(), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class RoundModel(Base):
    """Round table - tournament rounds within components."""

    __tablename__ = "rounds"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)

    # Foreign keys
    tournament_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("tournaments.id"), nullable=False
    )
    component_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("components.id"), nullable=False
    )

    round_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    scheduled_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scheduled_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    auto_advance: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class MatchModel(Base):
    """Match table - individual matches between players."""

    __tablename__ = "matches"

    id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)

    # Foreign keys
    tournament_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("tournaments.id"), nullable=False
    )
    component_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("components.id"), nullable=False
    )
    round_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("rounds.id"), nullable=False
    )
    player1_id: Mapped[PyUUID] = mapped_column(
        UUID(), ForeignKey("players.id"), nullable=False
    )
    player2_id: Mapped[PyUUID | None] = mapped_column(
        UUID(), ForeignKey("players.id"), nullable=True  # None for bye
    )

    round_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    table_number: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    player1_wins: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    player2_wins: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    draws: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
