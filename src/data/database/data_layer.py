"""Database data layer implementation.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.connection import DatabaseConnection
from src.data.database.repositories import (
    DatabaseComponentRepository,
    DatabaseFormatRepository,
    DatabaseMatchRepository,
    DatabasePlayerRepository,
    DatabaseRegistrationRepository,
    DatabaseRoundRepository,
    DatabaseTournamentRepository,
    DatabaseVenueRepository,
)
from src.data.interface import APIKeyRepository, DataLayer


class DatabaseDataLayer(DataLayer):
    """Database implementation of the data layer.

    Supports SQLite, PostgreSQL, MySQL, and MariaDB via SQLAlchemy.

    Example usage:
        # SQLite (file-based)
        data_layer = DatabaseDataLayer("sqlite+aiosqlite:///./tournament.db")

        # PostgreSQL
        data_layer = DatabaseDataLayer("postgresql+asyncpg://user:pass@localhost/tournament_director")

        # MySQL
        data_layer = DatabaseDataLayer("mysql+aiomysql://user:pass@localhost/tournament_director")

        # MariaDB
        data_layer = DatabaseDataLayer("mariadb+aiomysql://user:pass@localhost/tournament_director")

        # Initialize database tables
        await data_layer.initialize()

        # Use repositories
        players = await data_layer.players.list_all()

        # Remember to commit changes
        await data_layer.commit()

        # Clean up when done
        await data_layer.close()
    """

    def __init__(self, database_url: str) -> None:
        """Initialize database data layer.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.db = DatabaseConnection(database_url)
        self._session: AsyncSession | None = None
        self._players: DatabasePlayerRepository | None = None
        self._venues: DatabaseVenueRepository | None = None
        self._formats: DatabaseFormatRepository | None = None
        self._tournaments: DatabaseTournamentRepository | None = None
        self._registrations: DatabaseRegistrationRepository | None = None
        self._components: DatabaseComponentRepository | None = None
        self._rounds: DatabaseRoundRepository | None = None
        self._matches: DatabaseMatchRepository | None = None

    async def initialize(self) -> None:
        """Initialize database (create tables and session)."""
        await self.db.create_tables()
        # Create a long-lived session for repository access
        # Note: This matches the Mock/Local backend pattern
        self._session = self.db.async_session_maker()

        # Initialize repositories with the session
        self._players = DatabasePlayerRepository(self._session)
        self._venues = DatabaseVenueRepository(self._session)
        self._formats = DatabaseFormatRepository(self._session)
        self._tournaments = DatabaseTournamentRepository(self._session)
        self._registrations = DatabaseRegistrationRepository(self._session)
        self._components = DatabaseComponentRepository(self._session)
        self._rounds = DatabaseRoundRepository(self._session)
        self._matches = DatabaseMatchRepository(self._session)

    async def commit(self) -> None:
        """Commit pending changes to the database."""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Rollback pending changes."""
        if self._session:
            await self._session.rollback()

    async def close(self) -> None:
        """Close database connection and session."""
        if self._session:
            await self._session.close()
        await self.db.close()

    @property
    def players(self) -> DatabasePlayerRepository:
        """Access to player repository."""
        if not self._players:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._players

    @property
    def venues(self) -> DatabaseVenueRepository:
        """Access to venue repository."""
        if not self._venues:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._venues

    @property
    def formats(self) -> DatabaseFormatRepository:
        """Access to format repository."""
        if not self._formats:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._formats

    @property
    def tournaments(self) -> DatabaseTournamentRepository:
        """Access to tournament repository."""
        if not self._tournaments:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._tournaments

    @property
    def registrations(self) -> DatabaseRegistrationRepository:
        """Access to registration repository."""
        if not self._registrations:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._registrations

    @property
    def components(self) -> DatabaseComponentRepository:
        """Access to component repository."""
        if not self._components:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._components

    @property
    def rounds(self) -> DatabaseRoundRepository:
        """Access to round repository."""
        if not self._rounds:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._rounds

    @property
    def matches(self) -> DatabaseMatchRepository:
        """Access to match repository."""
        if not self._matches:
            raise RuntimeError(
                "DataLayer not initialized. Call await data_layer.initialize() first."
            )
        return self._matches

    @property
    def api_keys(self) -> APIKeyRepository:
        """Access to API key repository."""
        raise NotImplementedError("API key repository not yet implemented")

    async def seed_data(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """Seed the data layer with test/demo data.

        Args:
            data: Dictionary with entity type keys and lists of entity dicts
        """
        async with self.db.session() as session:
            # Create repositories with session
            player_repo = DatabasePlayerRepository(session)
            venue_repo = DatabaseVenueRepository(session)
            format_repo = DatabaseFormatRepository(session)
            tournament_repo = DatabaseTournamentRepository(session)
            registration_repo = DatabaseRegistrationRepository(session)
            component_repo = DatabaseComponentRepository(session)
            round_repo = DatabaseRoundRepository(session)
            match_repo = DatabaseMatchRepository(session)

            # Seed in dependency order
            from src.models.format import Format
            from src.models.match import Component, Match, Round
            from src.models.player import Player
            from src.models.tournament import Tournament, TournamentRegistration
            from src.models.venue import Venue

            # Players first (no dependencies)
            for player_dict in data.get("players", []):
                player = Player(**player_dict)
                await player_repo.create(player)

            # Venues (no dependencies)
            for venue_dict in data.get("venues", []):
                venue = Venue(**venue_dict)
                await venue_repo.create(venue)

            # Formats (no dependencies)
            for format_dict in data.get("formats", []):
                format_obj = Format(**format_dict)
                await format_repo.create(format_obj)

            # Tournaments (depend on players, venues, formats)
            for tournament_dict in data.get("tournaments", []):
                tournament = Tournament(**tournament_dict)
                await tournament_repo.create(tournament)

            # Registrations (depend on tournaments and players)
            for registration_dict in data.get("registrations", []):
                registration = TournamentRegistration(**registration_dict)
                await registration_repo.create(registration)

            # Components (depend on tournaments)
            for component_dict in data.get("components", []):
                component = Component(**component_dict)
                await component_repo.create(component)

            # Rounds (depend on tournaments and components)
            for round_dict in data.get("rounds", []):
                round_obj = Round(**round_dict)
                await round_repo.create(round_obj)

            # Matches (depend on everything)
            for match_dict in data.get("matches", []):
                match = Match(**match_dict)
                await match_repo.create(match)

            # Commit all changes
            await session.commit()

    async def clear_all_data(self) -> None:
        """Clear all data from the data layer. USE WITH CAUTION!"""
        await self.db.drop_tables()
        await self.db.create_tables()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check and return status information."""
        try:
            # Try to execute a simple query
            async with self.db.session() as session:
                from sqlalchemy import text

                result = await session.execute(text("SELECT 1"))
                result.fetchone()

            db_url = self.db.database_url
            masked_url = db_url.split("@")[-1] if "@" in db_url else db_url
            return {"status": "healthy", "database_url": masked_url, "connection": "active"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "connection": "failed"}
