"""Abstract interfaces for data layer repositories.

AIA PAI Hin R Claude Code v1.0
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.models.auth import APIKey
from src.models.format import Format
from src.models.match import Component, Match, Round
from src.models.player import Player
from src.models.tournament import Tournament, TournamentRegistration
from src.models.venue import Venue


class PlayerRepository(ABC):
    """Repository interface for Player entities."""

    @abstractmethod
    async def create(self, player: Player) -> Player:
        """Create a new player."""

    @abstractmethod
    async def get_by_id(self, player_id: UUID) -> Player:
        """Get player by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Player]:
        """Get player by name. Returns None if not found."""

    @abstractmethod
    async def get_by_discord_id(self, discord_id: str) -> Optional[Player]:
        """Get player by Discord ID. Returns None if not found."""

    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Player]:
        """List all players with optional pagination."""

    @abstractmethod
    async def update(self, player: Player) -> Player:
        """Update an existing player."""

    @abstractmethod
    async def delete(self, player_id: UUID) -> None:
        """Delete a player. Raises NotFoundError if not found."""


class VenueRepository(ABC):
    """Repository interface for Venue entities."""

    @abstractmethod
    async def create(self, venue: Venue) -> Venue:
        """Create a new venue."""

    @abstractmethod
    async def get_by_id(self, venue_id: UUID) -> Venue:
        """Get venue by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Venue]:
        """Get venue by name. Returns None if not found."""

    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Venue]:
        """List all venues with optional pagination."""

    @abstractmethod
    async def update(self, venue: Venue) -> Venue:
        """Update an existing venue."""

    @abstractmethod
    async def delete(self, venue_id: UUID) -> None:
        """Delete a venue. Raises NotFoundError if not found."""


class FormatRepository(ABC):
    """Repository interface for Format entities."""

    @abstractmethod
    async def create(self, format_obj: Format) -> Format:
        """Create a new format."""

    @abstractmethod
    async def get_by_id(self, format_id: UUID) -> Format:
        """Get format by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def get_by_name(self, name: str, game_system: Optional[str] = None) -> Optional[Format]:
        """Get format by name and optionally game system. Returns None if not found."""

    @abstractmethod
    async def list_by_game_system(self, game_system: str) -> List[Format]:
        """List all formats for a specific game system."""

    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Format]:
        """List all formats with optional pagination."""

    @abstractmethod
    async def update(self, format_obj: Format) -> Format:
        """Update an existing format."""

    @abstractmethod
    async def delete(self, format_id: UUID) -> None:
        """Delete a format. Raises NotFoundError if not found."""


class TournamentRepository(ABC):
    """Repository interface for Tournament entities."""

    @abstractmethod
    async def create(self, tournament: Tournament) -> Tournament:
        """Create a new tournament."""

    @abstractmethod
    async def get_by_id(self, tournament_id: UUID) -> Tournament:
        """Get tournament by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def list_by_status(self, status: str) -> List[Tournament]:
        """List tournaments by status."""

    @abstractmethod
    async def list_by_venue(self, venue_id: UUID) -> List[Tournament]:
        """List tournaments by venue."""

    @abstractmethod
    async def list_by_format(self, format_id: UUID) -> List[Tournament]:
        """List tournaments by format."""

    @abstractmethod
    async def list_by_organizer(self, organizer_id: UUID) -> List[Tournament]:
        """List tournaments by organizer (created_by)."""

    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Tournament]:
        """List all tournaments with optional pagination."""

    @abstractmethod
    async def update(self, tournament: Tournament) -> Tournament:
        """Update an existing tournament."""

    @abstractmethod
    async def delete(self, tournament_id: UUID) -> None:
        """Delete a tournament. Raises NotFoundError if not found."""


class RegistrationRepository(ABC):
    """Repository interface for TournamentRegistration entities."""

    @abstractmethod
    async def create(self, registration: TournamentRegistration) -> TournamentRegistration:
        """Create a new tournament registration."""

    @abstractmethod
    async def get_by_id(self, registration_id: UUID) -> TournamentRegistration:
        """Get registration by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def get_by_tournament_and_player(self, tournament_id: UUID, player_id: UUID) -> Optional[TournamentRegistration]:
        """Get registration by tournament and player. Returns None if not found."""

    @abstractmethod
    async def get_by_tournament_and_sequence_id(self, tournament_id: UUID, sequence_id: int) -> Optional[TournamentRegistration]:
        """Get registration by tournament and sequence ID. Returns None if not found."""

    @abstractmethod
    async def list_by_tournament(self, tournament_id: UUID, status: Optional[str] = None) -> List[TournamentRegistration]:
        """List registrations for a tournament, optionally filtered by status."""

    @abstractmethod
    async def list_by_player(self, player_id: UUID, status: Optional[str] = None) -> List[TournamentRegistration]:
        """List registrations for a player, optionally filtered by status."""

    @abstractmethod
    async def get_next_sequence_id(self, tournament_id: UUID) -> int:
        """Get the next available sequence ID for a tournament."""

    @abstractmethod
    async def update(self, registration: TournamentRegistration) -> TournamentRegistration:
        """Update an existing registration."""

    @abstractmethod
    async def delete(self, registration_id: UUID) -> None:
        """Delete a registration. Raises NotFoundError if not found."""


class ComponentRepository(ABC):
    """Repository interface for Component entities."""

    @abstractmethod
    async def create(self, component: Component) -> Component:
        """Create a new component."""

    @abstractmethod
    async def get_by_id(self, component_id: UUID) -> Component:
        """Get component by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def list_by_tournament(self, tournament_id: UUID) -> List[Component]:
        """List components for a tournament, ordered by sequence_order."""

    @abstractmethod
    async def get_by_tournament_and_sequence(self, tournament_id: UUID, sequence_order: int) -> Optional[Component]:
        """Get component by tournament and sequence order. Returns None if not found."""

    @abstractmethod
    async def update(self, component: Component) -> Component:
        """Update an existing component."""

    @abstractmethod
    async def delete(self, component_id: UUID) -> None:
        """Delete a component. Raises NotFoundError if not found."""


class RoundRepository(ABC):
    """Repository interface for Round entities."""

    @abstractmethod
    async def create(self, round_obj: Round) -> Round:
        """Create a new round."""

    @abstractmethod
    async def get_by_id(self, round_id: UUID) -> Round:
        """Get round by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def list_by_tournament(self, tournament_id: UUID) -> List[Round]:
        """List rounds for a tournament, ordered by component sequence and round number."""

    @abstractmethod
    async def list_by_component(self, component_id: UUID) -> List[Round]:
        """List rounds for a component, ordered by round number."""

    @abstractmethod
    async def get_by_component_and_round_number(self, component_id: UUID, round_number: int) -> Optional[Round]:
        """Get round by component and round number. Returns None if not found."""

    @abstractmethod
    async def update(self, round_obj: Round) -> Round:
        """Update an existing round."""

    @abstractmethod
    async def delete(self, round_id: UUID) -> None:
        """Delete a round. Raises NotFoundError if not found."""


class MatchRepository(ABC):
    """Repository interface for Match entities."""

    @abstractmethod
    async def create(self, match: Match) -> Match:
        """Create a new match."""

    @abstractmethod
    async def get_by_id(self, match_id: UUID) -> Match:
        """Get match by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def list_by_tournament(self, tournament_id: UUID) -> List[Match]:
        """List matches for a tournament, ordered by round number."""

    @abstractmethod
    async def list_by_round(self, round_id: UUID) -> List[Match]:
        """List matches for a round, ordered by table number."""

    @abstractmethod
    async def list_by_component(self, component_id: UUID) -> List[Match]:
        """List matches for a component, ordered by round and table number."""

    @abstractmethod
    async def list_by_player(self, player_id: UUID, tournament_id: Optional[UUID] = None) -> List[Match]:
        """List matches for a player, optionally filtered by tournament."""

    @abstractmethod
    async def update(self, match: Match) -> Match:
        """Update an existing match."""

    @abstractmethod
    async def delete(self, match_id: UUID) -> None:
        """Delete a match. Raises NotFoundError if not found."""


class APIKeyRepository(ABC):
    """Repository interface for APIKey entities."""

    @abstractmethod
    async def create(self, api_key: APIKey) -> APIKey:
        """Create a new API key."""

    @abstractmethod
    async def get_by_id(self, key_id: UUID) -> APIKey:
        """Get API key by ID. Raises NotFoundError if not found."""

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[APIKey]:
        """Get API key by token value. Returns None if not found."""

    @abstractmethod
    async def list_by_owner(self, player_id: UUID) -> List[APIKey]:
        """List all API keys for a player, ordered by created_at descending."""

    @abstractmethod
    async def update(self, api_key: APIKey) -> APIKey:
        """Update an existing API key."""

    @abstractmethod
    async def delete(self, key_id: UUID) -> None:
        """Delete an API key. Raises NotFoundError if not found."""


class DataLayer(ABC):
    """Main data layer interface providing access to all repositories."""

    @property
    @abstractmethod
    def players(self) -> PlayerRepository:
        """Access to player repository."""

    @property
    @abstractmethod
    def venues(self) -> VenueRepository:
        """Access to venue repository."""

    @property
    @abstractmethod
    def formats(self) -> FormatRepository:
        """Access to format repository."""

    @property
    @abstractmethod
    def tournaments(self) -> TournamentRepository:
        """Access to tournament repository."""

    @property
    @abstractmethod
    def registrations(self) -> RegistrationRepository:
        """Access to registration repository."""

    @property
    @abstractmethod
    def components(self) -> ComponentRepository:
        """Access to component repository."""

    @property
    @abstractmethod
    def rounds(self) -> RoundRepository:
        """Access to round repository."""

    @property
    @abstractmethod
    def matches(self) -> MatchRepository:
        """Access to match repository."""

    @property
    @abstractmethod
    def api_keys(self) -> APIKeyRepository:
        """Access to API key repository."""

    @abstractmethod
    async def seed_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Seed the data layer with test/demo data."""

    @abstractmethod
    async def clear_all_data(self) -> None:
        """Clear all data from the data layer. Use with caution!"""

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status information."""
