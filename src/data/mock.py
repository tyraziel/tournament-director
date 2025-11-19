"""Mock backend implementation using in-memory storage.

AIA PAI Hin R Claude Code v1.0
"""

from typing import Any
from uuid import UUID

from src.models.auth import APIKey
from src.models.format import Format
from src.models.match import Component, Match, Round
from src.models.player import Player
from src.models.tournament import Tournament, TournamentRegistration
from src.models.venue import Venue

from .exceptions import DuplicateError, NotFoundError
from .interface import (
    APIKeyRepository,
    ComponentRepository,
    DataLayer,
    FormatRepository,
    MatchRepository,
    PlayerRepository,
    RegistrationRepository,
    RoundRepository,
    TournamentRepository,
    VenueRepository,
)


class MockPlayerRepository(PlayerRepository):
    """Mock implementation of PlayerRepository."""

    def __init__(self) -> None:
        self._players: dict[UUID, Player] = {}

    async def create(self, player: Player) -> Player:
        if player.id in self._players:
            raise DuplicateError("Player", "id", player.id)

        # Check for duplicate name
        for existing in self._players.values():
            if existing.name == player.name:
                raise DuplicateError("Player", "name", player.name)

        self._players[player.id] = player
        return player

    async def get_by_id(self, player_id: UUID) -> Player:
        if player_id not in self._players:
            raise NotFoundError("Player", player_id)
        return self._players[player_id]

    async def get_by_name(self, name: str) -> Player | None:
        for player in self._players.values():
            if player.name == name:
                return player
        return None

    async def get_by_discord_id(self, discord_id: str) -> Player | None:
        for player in self._players.values():
            if player.discord_id == discord_id:
                return player
        return None

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[Player]:
        players = list(self._players.values())
        players.sort(key=lambda p: p.created_at)

        if offset >= len(players):
            return []

        end_idx = offset + limit if limit else len(players)
        return players[offset:end_idx]

    async def update(self, player: Player) -> Player:
        if player.id not in self._players:
            raise NotFoundError("Player", player.id)

        # Check for duplicate name (excluding self)
        for existing in self._players.values():
            if existing.id != player.id and existing.name == player.name:
                raise DuplicateError("Player", "name", player.name)

        self._players[player.id] = player
        return player

    async def delete(self, player_id: UUID) -> None:
        if player_id not in self._players:
            raise NotFoundError("Player", player_id)
        del self._players[player_id]


class MockVenueRepository(VenueRepository):
    """Mock implementation of VenueRepository."""

    def __init__(self) -> None:
        self._venues: dict[UUID, Venue] = {}

    async def create(self, venue: Venue) -> Venue:
        if venue.id in self._venues:
            raise DuplicateError("Venue", "id", venue.id)

        self._venues[venue.id] = venue
        return venue

    async def get_by_id(self, venue_id: UUID) -> Venue:
        if venue_id not in self._venues:
            raise NotFoundError("Venue", venue_id)
        return self._venues[venue_id]

    async def get_by_name(self, name: str) -> Venue | None:
        for venue in self._venues.values():
            if venue.name == name:
                return venue
        return None

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[Venue]:
        venues = list(self._venues.values())
        venues.sort(key=lambda v: v.name)

        if offset >= len(venues):
            return []

        end_idx = offset + limit if limit else len(venues)
        return venues[offset:end_idx]

    async def update(self, venue: Venue) -> Venue:
        if venue.id not in self._venues:
            raise NotFoundError("Venue", venue.id)

        self._venues[venue.id] = venue
        return venue

    async def delete(self, venue_id: UUID) -> None:
        if venue_id not in self._venues:
            raise NotFoundError("Venue", venue_id)
        del self._venues[venue_id]


class MockFormatRepository(FormatRepository):
    """Mock implementation of FormatRepository."""

    def __init__(self) -> None:
        self._formats: dict[UUID, Format] = {}

    async def create(self, format_obj: Format) -> Format:
        if format_obj.id in self._formats:
            raise DuplicateError("Format", "id", format_obj.id)

        # Check for duplicate name within game system
        for existing in self._formats.values():
            if existing.name == format_obj.name and existing.game_system == format_obj.game_system:
                raise DuplicateError(
                    "Format", "name+game_system", f"{format_obj.name}+{format_obj.game_system}"
                )

        self._formats[format_obj.id] = format_obj
        return format_obj

    async def get_by_id(self, format_id: UUID) -> Format:
        if format_id not in self._formats:
            raise NotFoundError("Format", format_id)
        return self._formats[format_id]

    async def get_by_name(self, name: str, game_system: str | None = None) -> Format | None:
        for format_obj in self._formats.values():
            if format_obj.name == name and (
                game_system is None or format_obj.game_system == game_system
            ):
                return format_obj
        return None

    async def list_by_game_system(self, game_system: str) -> list[Format]:
        formats = [f for f in self._formats.values() if f.game_system == game_system]
        formats.sort(key=lambda f: f.name)
        return formats

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[Format]:
        formats = list(self._formats.values())
        formats.sort(key=lambda f: (f.game_system.value, f.name))

        if offset >= len(formats):
            return []

        end_idx = offset + limit if limit else len(formats)
        return formats[offset:end_idx]

    async def update(self, format_obj: Format) -> Format:
        if format_obj.id not in self._formats:
            raise NotFoundError("Format", format_obj.id)

        # Check for duplicate name within game system (excluding self)
        for existing in self._formats.values():
            if (
                existing.id != format_obj.id
                and existing.name == format_obj.name
                and existing.game_system == format_obj.game_system
            ):
                raise DuplicateError(
                    "Format", "name+game_system", f"{format_obj.name}+{format_obj.game_system}"
                )

        self._formats[format_obj.id] = format_obj
        return format_obj

    async def delete(self, format_id: UUID) -> None:
        if format_id not in self._formats:
            raise NotFoundError("Format", format_id)
        del self._formats[format_id]


class MockTournamentRepository(TournamentRepository):
    """Mock implementation of TournamentRepository."""

    def __init__(
        self,
        player_repo: MockPlayerRepository,
        venue_repo: MockVenueRepository,
        format_repo: MockFormatRepository,
    ) -> None:
        self._tournaments: dict[UUID, Tournament] = {}
        self._player_repo = player_repo
        self._venue_repo = venue_repo
        self._format_repo = format_repo

    async def create(self, tournament: Tournament) -> Tournament:
        if tournament.id in self._tournaments:
            raise DuplicateError("Tournament", "id", tournament.id)

        # Validate foreign keys
        # Will raise NotFoundError if invalid
        await self._player_repo.get_by_id(tournament.created_by)
        await self._venue_repo.get_by_id(tournament.venue_id)
        await self._format_repo.get_by_id(tournament.format_id)

        self._tournaments[tournament.id] = tournament
        return tournament

    async def get_by_id(self, tournament_id: UUID) -> Tournament:
        if tournament_id not in self._tournaments:
            raise NotFoundError("Tournament", tournament_id)
        return self._tournaments[tournament_id]

    async def list_by_status(self, status: str) -> list[Tournament]:
        tournaments = [t for t in self._tournaments.values() if t.status == status]
        tournaments.sort(key=lambda t: t.created_at, reverse=True)
        return tournaments

    async def list_by_venue(self, venue_id: UUID) -> list[Tournament]:
        tournaments = [t for t in self._tournaments.values() if t.venue_id == venue_id]
        tournaments.sort(key=lambda t: t.created_at, reverse=True)
        return tournaments

    async def list_by_format(self, format_id: UUID) -> list[Tournament]:
        tournaments = [t for t in self._tournaments.values() if t.format_id == format_id]
        tournaments.sort(key=lambda t: t.created_at, reverse=True)
        return tournaments

    async def list_by_organizer(self, organizer_id: UUID) -> list[Tournament]:
        tournaments = [t for t in self._tournaments.values() if t.created_by == organizer_id]
        tournaments.sort(key=lambda t: t.created_at, reverse=True)
        return tournaments

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[Tournament]:
        tournaments = list(self._tournaments.values())
        tournaments.sort(key=lambda t: t.created_at, reverse=True)

        if offset >= len(tournaments):
            return []

        end_idx = offset + limit if limit else len(tournaments)
        return tournaments[offset:end_idx]

    async def update(self, tournament: Tournament) -> Tournament:
        if tournament.id not in self._tournaments:
            raise NotFoundError("Tournament", tournament.id)

        # Validate foreign keys
        await self._player_repo.get_by_id(tournament.created_by)
        await self._venue_repo.get_by_id(tournament.venue_id)
        await self._format_repo.get_by_id(tournament.format_id)

        self._tournaments[tournament.id] = tournament
        return tournament

    async def delete(self, tournament_id: UUID) -> None:
        if tournament_id not in self._tournaments:
            raise NotFoundError("Tournament", tournament_id)
        del self._tournaments[tournament_id]


class MockRegistrationRepository(RegistrationRepository):
    """Mock implementation of RegistrationRepository."""

    def __init__(
        self, tournament_repo: MockTournamentRepository, player_repo: MockPlayerRepository
    ) -> None:
        self._registrations: dict[UUID, TournamentRegistration] = {}
        self._tournament_repo = tournament_repo
        self._player_repo = player_repo

    async def create(self, registration: TournamentRegistration) -> TournamentRegistration:
        if registration.id in self._registrations:
            raise DuplicateError("TournamentRegistration", "id", registration.id)

        # Validate foreign keys
        await self._tournament_repo.get_by_id(registration.tournament_id)
        await self._player_repo.get_by_id(registration.player_id)

        # Check for duplicate registration
        for existing in self._registrations.values():
            if (
                existing.tournament_id == registration.tournament_id
                and existing.player_id == registration.player_id
            ):
                raise DuplicateError(
                    "TournamentRegistration",
                    "tournament+player",
                    f"{registration.tournament_id}+{registration.player_id}",
                )

        # Check for duplicate sequence ID
        for existing in self._registrations.values():
            if (
                existing.tournament_id == registration.tournament_id
                and existing.sequence_id == registration.sequence_id
            ):
                raise DuplicateError(
                    "TournamentRegistration",
                    "tournament+sequence_id",
                    f"{registration.tournament_id}+{registration.sequence_id}",
                )

        self._registrations[registration.id] = registration
        return registration

    async def get_by_id(self, registration_id: UUID) -> TournamentRegistration:
        if registration_id not in self._registrations:
            raise NotFoundError("TournamentRegistration", registration_id)
        return self._registrations[registration_id]

    async def get_by_tournament_and_player(
        self, tournament_id: UUID, player_id: UUID
    ) -> TournamentRegistration | None:
        for registration in self._registrations.values():
            if registration.tournament_id == tournament_id and registration.player_id == player_id:
                return registration
        return None

    async def get_by_tournament_and_sequence_id(
        self, tournament_id: UUID, sequence_id: int
    ) -> TournamentRegistration | None:
        for registration in self._registrations.values():
            if (
                registration.tournament_id == tournament_id
                and registration.sequence_id == sequence_id
            ):
                return registration
        return None

    async def list_by_tournament(
        self, tournament_id: UUID, status: str | None = None
    ) -> list[TournamentRegistration]:
        registrations = [
            r for r in self._registrations.values() if r.tournament_id == tournament_id
        ]

        if status:
            registrations = [r for r in registrations if r.status == status]

        registrations.sort(key=lambda r: r.sequence_id)
        return registrations

    async def list_by_player(
        self, player_id: UUID, status: str | None = None
    ) -> list[TournamentRegistration]:
        registrations = [r for r in self._registrations.values() if r.player_id == player_id]

        if status:
            registrations = [r for r in registrations if r.status == status]

        registrations.sort(key=lambda r: r.registration_time, reverse=True)
        return registrations

    async def get_next_sequence_id(self, tournament_id: UUID) -> int:
        max_sequence_id = 0
        for registration in self._registrations.values():
            if (
                registration.tournament_id == tournament_id
                and registration.sequence_id > max_sequence_id
            ):
                max_sequence_id = registration.sequence_id
        return max_sequence_id + 1

    async def update(self, registration: TournamentRegistration) -> TournamentRegistration:
        if registration.id not in self._registrations:
            raise NotFoundError("TournamentRegistration", registration.id)

        # Validate foreign keys
        await self._tournament_repo.get_by_id(registration.tournament_id)
        await self._player_repo.get_by_id(registration.player_id)

        # Check for duplicate sequence ID (excluding self)
        for existing in self._registrations.values():
            if (
                existing.id != registration.id
                and existing.tournament_id == registration.tournament_id
                and existing.sequence_id == registration.sequence_id
            ):
                raise DuplicateError(
                    "TournamentRegistration",
                    "tournament+sequence_id",
                    f"{registration.tournament_id}+{registration.sequence_id}",
                )

        self._registrations[registration.id] = registration
        return registration

    async def delete(self, registration_id: UUID) -> None:
        if registration_id not in self._registrations:
            raise NotFoundError("TournamentRegistration", registration_id)
        del self._registrations[registration_id]


# Additional repositories would follow the same pattern...
# For brevity, I'll implement a basic version and we can expand later


class MockComponentRepository(ComponentRepository):
    def __init__(self, tournament_repo: MockTournamentRepository) -> None:
        self._components: dict[UUID, Component] = {}
        self._tournament_repo = tournament_repo

    async def create(self, component: Component) -> Component:
        await self._tournament_repo.get_by_id(component.tournament_id)  # Validate FK
        self._components[component.id] = component
        return component

    async def get_by_id(self, component_id: UUID) -> Component:
        if component_id not in self._components:
            raise NotFoundError("Component", component_id)
        return self._components[component_id]

    async def list_by_tournament(self, tournament_id: UUID) -> list[Component]:
        components = [c for c in self._components.values() if c.tournament_id == tournament_id]
        components.sort(key=lambda c: c.sequence_order)
        return components

    async def get_by_tournament_and_sequence(
        self, tournament_id: UUID, sequence_order: int
    ) -> Component | None:
        for component in self._components.values():
            if (
                component.tournament_id == tournament_id
                and component.sequence_order == sequence_order
            ):
                return component
        return None

    async def update(self, component: Component) -> Component:
        if component.id not in self._components:
            raise NotFoundError("Component", component.id)
        self._components[component.id] = component
        return component

    async def delete(self, component_id: UUID) -> None:
        if component_id not in self._components:
            raise NotFoundError("Component", component_id)
        del self._components[component_id]


class MockRoundRepository(RoundRepository):
    def __init__(
        self, tournament_repo: MockTournamentRepository, component_repo: MockComponentRepository
    ) -> None:
        self._rounds: dict[UUID, Round] = {}
        self._tournament_repo = tournament_repo
        self._component_repo = component_repo

    async def create(self, round_obj: Round) -> Round:
        await self._tournament_repo.get_by_id(round_obj.tournament_id)  # Validate FK
        await self._component_repo.get_by_id(round_obj.component_id)  # Validate FK
        self._rounds[round_obj.id] = round_obj
        return round_obj

    async def get_by_id(self, round_id: UUID) -> Round:
        if round_id not in self._rounds:
            raise NotFoundError("Round", round_id)
        return self._rounds[round_id]

    async def list_by_tournament(self, tournament_id: UUID) -> list[Round]:
        rounds = [r for r in self._rounds.values() if r.tournament_id == tournament_id]
        rounds.sort(key=lambda r: r.round_number)
        return rounds

    async def list_by_component(self, component_id: UUID) -> list[Round]:
        rounds = [r for r in self._rounds.values() if r.component_id == component_id]
        rounds.sort(key=lambda r: r.round_number)
        return rounds

    async def get_by_component_and_round_number(
        self, component_id: UUID, round_number: int
    ) -> Round | None:
        for round_obj in self._rounds.values():
            if round_obj.component_id == component_id and round_obj.round_number == round_number:
                return round_obj
        return None

    async def update(self, round_obj: Round) -> Round:
        if round_obj.id not in self._rounds:
            raise NotFoundError("Round", round_obj.id)
        self._rounds[round_obj.id] = round_obj
        return round_obj

    async def delete(self, round_id: UUID) -> None:
        if round_id not in self._rounds:
            raise NotFoundError("Round", round_id)
        del self._rounds[round_id]


class MockMatchRepository(MatchRepository):
    def __init__(
        self,
        tournament_repo: MockTournamentRepository,
        component_repo: MockComponentRepository,
        round_repo: MockRoundRepository,
        player_repo: MockPlayerRepository,
    ) -> None:
        self._matches: dict[UUID, Match] = {}
        self._tournament_repo = tournament_repo
        self._component_repo = component_repo
        self._round_repo = round_repo
        self._player_repo = player_repo

    async def create(self, match: Match) -> Match:
        # Validate foreign keys
        await self._tournament_repo.get_by_id(match.tournament_id)
        await self._component_repo.get_by_id(match.component_id)
        await self._round_repo.get_by_id(match.round_id)
        await self._player_repo.get_by_id(match.player1_id)
        if match.player2_id:  # Can be None for bye
            await self._player_repo.get_by_id(match.player2_id)

        self._matches[match.id] = match
        return match

    async def get_by_id(self, match_id: UUID) -> Match:
        if match_id not in self._matches:
            raise NotFoundError("Match", match_id)
        return self._matches[match_id]

    async def list_by_tournament(self, tournament_id: UUID) -> list[Match]:
        matches = [m for m in self._matches.values() if m.tournament_id == tournament_id]
        matches.sort(key=lambda m: (m.round_number, m.table_number or 0))
        return matches

    async def list_by_round(self, round_id: UUID) -> list[Match]:
        matches = [m for m in self._matches.values() if m.round_id == round_id]
        matches.sort(key=lambda m: m.table_number or 0)
        return matches

    async def list_by_component(self, component_id: UUID) -> list[Match]:
        matches = [m for m in self._matches.values() if m.component_id == component_id]
        matches.sort(key=lambda m: (m.round_number, m.table_number or 0))
        return matches

    async def list_by_player(
        self, player_id: UUID, tournament_id: UUID | None = None
    ) -> list[Match]:
        matches = [
            m
            for m in self._matches.values()
            if m.player1_id == player_id or m.player2_id == player_id
        ]

        if tournament_id:
            matches = [m for m in matches if m.tournament_id == tournament_id]

        matches.sort(key=lambda m: (m.round_number, m.table_number or 0))
        return matches

    async def update(self, match: Match) -> Match:
        if match.id not in self._matches:
            raise NotFoundError("Match", match.id)
        self._matches[match.id] = match
        return match

    async def delete(self, match_id: UUID) -> None:
        if match_id not in self._matches:
            raise NotFoundError("Match", match_id)
        del self._matches[match_id]


class MockAPIKeyRepository(APIKeyRepository):
    """Mock implementation of APIKeyRepository."""

    def __init__(self) -> None:
        self._api_keys: dict[UUID, APIKey] = {}
        self._token_index: dict[str, UUID] = {}  # token -> api_key_id

    async def create(self, api_key: APIKey) -> APIKey:
        if api_key.id in self._api_keys:
            raise DuplicateError("APIKey", "id", api_key.id)

        # Check for duplicate token
        if api_key.token in self._token_index:
            raise DuplicateError("APIKey", "token", api_key.token)

        self._api_keys[api_key.id] = api_key
        self._token_index[api_key.token] = api_key.id
        return api_key

    async def get_by_id(self, key_id: UUID) -> APIKey:
        if key_id not in self._api_keys:
            raise NotFoundError("APIKey", key_id)
        return self._api_keys[key_id]

    async def get_by_token(self, token: str) -> APIKey | None:
        key_id = self._token_index.get(token)
        if not key_id:
            return None
        return self._api_keys.get(key_id)

    async def list_by_owner(self, player_id: UUID) -> list[APIKey]:
        keys = [key for key in self._api_keys.values() if key.created_by == player_id]
        keys.sort(key=lambda k: k.created_at, reverse=True)
        return keys

    async def update(self, api_key: APIKey) -> APIKey:
        if api_key.id not in self._api_keys:
            raise NotFoundError("APIKey", api_key.id)

        # If token changed, update index
        old_api_key = self._api_keys[api_key.id]
        if old_api_key.token != api_key.token:
            # Remove old token from index
            del self._token_index[old_api_key.token]
            # Check for duplicate new token
            if api_key.token in self._token_index:
                raise DuplicateError("APIKey", "token", api_key.token)
            # Add new token to index
            self._token_index[api_key.token] = api_key.id

        self._api_keys[api_key.id] = api_key
        return api_key

    async def delete(self, key_id: UUID) -> None:
        if key_id not in self._api_keys:
            raise NotFoundError("APIKey", key_id)

        api_key = self._api_keys[key_id]
        del self._token_index[api_key.token]
        del self._api_keys[key_id]


class MockDataLayer(DataLayer):
    """Mock implementation of the complete data layer."""

    def __init__(self) -> None:
        # Initialize repositories in dependency order
        self._player_repo = MockPlayerRepository()
        self._venue_repo = MockVenueRepository()
        self._format_repo = MockFormatRepository()
        self._tournament_repo = MockTournamentRepository(
            self._player_repo, self._venue_repo, self._format_repo
        )
        self._registration_repo = MockRegistrationRepository(
            self._tournament_repo, self._player_repo
        )
        self._component_repo = MockComponentRepository(self._tournament_repo)
        self._round_repo = MockRoundRepository(self._tournament_repo, self._component_repo)
        self._match_repo = MockMatchRepository(
            self._tournament_repo, self._component_repo, self._round_repo, self._player_repo
        )
        self._api_key_repo = MockAPIKeyRepository()

    @property
    def players(self) -> PlayerRepository:
        return self._player_repo

    @property
    def venues(self) -> VenueRepository:
        return self._venue_repo

    @property
    def formats(self) -> FormatRepository:
        return self._format_repo

    @property
    def tournaments(self) -> TournamentRepository:
        return self._tournament_repo

    @property
    def registrations(self) -> RegistrationRepository:
        return self._registration_repo

    @property
    def components(self) -> ComponentRepository:
        return self._component_repo

    @property
    def rounds(self) -> RoundRepository:
        return self._round_repo

    @property
    def matches(self) -> MatchRepository:
        return self._match_repo

    @property
    def api_keys(self) -> APIKeyRepository:
        return self._api_key_repo

    async def seed_data(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """Seed the data layer with test/demo data."""
        # Clear existing data first
        await self.clear_all_data()

        # Import data in dependency order
        model_classes = {
            "players": Player,
            "venues": Venue,
            "formats": Format,
            "tournaments": Tournament,
            "registrations": TournamentRegistration,
            "components": Component,
            "rounds": Round,
            "matches": Match,
        }

        repositories = {
            "players": self.players,
            "venues": self.venues,
            "formats": self.formats,
            "tournaments": self.tournaments,
            "registrations": self.registrations,
            "components": self.components,
            "rounds": self.rounds,
            "matches": self.matches,
        }

        for entity_type, entity_list in data.items():
            if entity_type in model_classes and entity_list:
                model_class = model_classes[entity_type]
                repository = repositories[entity_type]

                for entity_data in entity_list:
                    # Convert dict to Pydantic model
                    entity = model_class.model_validate(entity_data)  # type: ignore[attr-defined]
                    await repository.create(entity)  # type: ignore[attr-defined]

    async def clear_all_data(self) -> None:
        """Clear all data from the data layer."""
        # Clear in reverse dependency order
        self._match_repo._matches.clear()
        self._round_repo._rounds.clear()
        self._component_repo._components.clear()
        self._registration_repo._registrations.clear()
        self._tournament_repo._tournaments.clear()
        self._format_repo._formats.clear()
        self._venue_repo._venues.clear()
        self._player_repo._players.clear()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check and return status information."""
        return {
            "backend_type": "mock",
            "status": "healthy",
            "entities": {
                "players": len(self._player_repo._players),
                "venues": len(self._venue_repo._venues),
                "formats": len(self._format_repo._formats),
                "tournaments": len(self._tournament_repo._tournaments),
                "registrations": len(self._registration_repo._registrations),
                "components": len(self._component_repo._components),
                "rounds": len(self._round_repo._rounds),
                "matches": len(self._match_repo._matches),
            },
        }
