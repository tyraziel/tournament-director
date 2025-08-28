"""Seed data generators for Tournament Director backend testing.

AIA PAI Hin R Claude Code v1.0
"""

from typing import Any, Dict, List
from uuid import uuid4

from src.models.format import Format
from src.models.match import Component, Match, Round
from src.models.player import Player
from src.models.tournament import RegistrationControl, Tournament, TournamentRegistration
from src.models.venue import Venue


class SeedDataGenerator:
    """Generate realistic tournament data for testing backends."""

    def __init__(self):
        self.players = {}
        self.venues = {}
        self.formats = {}
        self.tournaments = {}
        self.registrations = {}
        self.components = {}
        self.rounds = {}
        self.matches = {}

    def reset(self):
        """Clear all generated data."""
        self.__init__()

    def add_player(self, name: str, discord_id: str = None, email: str = None) -> Player:
        """Add a player to the seed data."""
        player = Player(
            id=uuid4(),
            name=name,
            discord_id=discord_id,
            email=email
        )
        self.players[player.id] = player
        return player

    def add_venue(self, name: str, address: str = None, description: str = None) -> Venue:
        """Add a venue to the seed data."""
        venue = Venue(
            id=uuid4(),
            name=name,
            address=address,
            description=description
        )
        self.venues[venue.id] = venue
        return venue

    def add_format(self, name: str, game_system: str, base_format: str,
                  sub_format: str = None, card_pool: str = None,
                  match_structure: str = None, description: str = None) -> Format:
        """Add a format to the seed data."""
        format_obj = Format(
            id=uuid4(),
            name=name,
            game_system=game_system,
            base_format=base_format,
            sub_format=sub_format,
            card_pool=card_pool or name,
            match_structure=match_structure,
            description=description
        )
        self.formats[format_obj.id] = format_obj
        return format_obj

    def add_tournament(self, name: str, format_obj: Format, venue: Venue,
                      created_by: Player, status: str = "draft",
                      visibility: str = "public", description: str = None,
                      max_players: int = None) -> Tournament:
        """Add a tournament to the seed data."""
        tournament = Tournament(
            id=uuid4(),
            name=name,
            status=status,
            visibility=visibility,
            registration=RegistrationControl(
                max_players=max_players,
                allow_to_override=True
            ),
            format_id=format_obj.id,
            venue_id=venue.id,
            created_by=created_by.id,
            description=description
        )
        self.tournaments[tournament.id] = tournament
        return tournament

    def register_player(self, tournament: Tournament, player: Player,
                       sequence_id: int, status: str = "active") -> TournamentRegistration:
        """Register a player for a tournament."""
        registration = TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament.id,
            player_id=player.id,
            sequence_id=sequence_id,
            status=status
        )
        self.registrations[registration.id] = registration
        return registration

    def add_component(self, tournament: Tournament, component_type: str,
                     name: str, sequence_order: int,
                     config: Dict[str, Any] = None) -> Component:
        """Add a tournament component."""
        component = Component(
            id=uuid4(),
            tournament_id=tournament.id,
            type=component_type,
            name=name,
            sequence_order=sequence_order,
            config=config or {}
        )
        self.components[component.id] = component
        return component

    def add_round(self, tournament: Tournament, component: Component,
                 round_number: int, time_limit_minutes: int = None,
                 status: str = "pending") -> Round:
        """Add a tournament round."""
        round_obj = Round(
            id=uuid4(),
            tournament_id=tournament.id,
            component_id=component.id,
            round_number=round_number,
            time_limit_minutes=time_limit_minutes,
            status=status
        )
        self.rounds[round_obj.id] = round_obj
        return round_obj

    def add_match(self, tournament: Tournament, component: Component,
                 round_obj: Round, player1: Player, player2: Player = None,
                 table_number: int = None, player1_wins: int = 0,
                 player2_wins: int = 0, draws: int = 0,
                 notes: str = None) -> Match:
        """Add a match result."""
        match = Match(
            id=uuid4(),
            tournament_id=tournament.id,
            component_id=component.id,
            round_id=round_obj.id,
            round_number=round_obj.round_number,
            table_number=table_number,
            player1_id=player1.id,
            player2_id=player2.id if player2 else None,
            player1_wins=player1_wins,
            player2_wins=player2_wins,
            draws=draws,
            notes=notes
        )
        self.matches[match.id] = match
        return match

    def to_dict(self) -> Dict[str, List[Dict]]:
        """Export all seed data as serializable dictionary."""
        return {
            "players": [p.model_dump() for p in self.players.values()],
            "venues": [v.model_dump() for v in self.venues.values()],
            "formats": [f.model_dump() for f in self.formats.values()],
            "tournaments": [t.model_dump() for t in self.tournaments.values()],
            "registrations": [r.model_dump() for r in self.registrations.values()],
            "components": [c.model_dump() for c in self.components.values()],
            "rounds": [r.model_dump() for r in self.rounds.values()],
            "matches": [m.model_dump() for m in self.matches.values()]
        }


def generate_kitchen_table_pauper() -> SeedDataGenerator:
    """Generate Kitchen Table Pauper Championship scenario."""
    gen = SeedDataGenerator()

    # Create venues and formats
    kitchen_table = gen.add_venue(
        "Kitchen Table",
        description="Home casual play"
    )

    pauper_format = gen.add_format(
        "Pauper",
        game_system="magic_the_gathering",
        base_format="constructed",
        sub_format="Pauper",
        card_pool="Pauper",
        match_structure="BO3"
    )

    # Create players
    players = [
        gen.add_player("Andrew", "andrew#1234", "andrew@example.com"),
        gen.add_player("Bob", "bob#5678"),
        gen.add_player("Charlie", email="charlie@example.com"),
        gen.add_player("Dana"),
        gen.add_player("Eve", "eve#9999"),
        gen.add_player("Frank", "frank#1111", "frank@example.com"),
        gen.add_player("Grace"),
        gen.add_player("Henry", "henry#2222")
    ]

    # Create tournament
    tournament = gen.add_tournament(
        "Kitchen Table Pauper Championship",
        pauper_format,
        kitchen_table,
        players[0],  # Andrew is the TO
        status="in_progress",
        description="Monthly Pauper tournament at the kitchen table",
        max_players=8
    )

    # Register all players
    for i, player in enumerate(players):
        gen.register_player(tournament, player, i + 1)

    # Create Swiss component (3 rounds)
    swiss = gen.add_component(
        tournament,
        "swiss",
        "Swiss Rounds",
        1,
        {"rounds": 3, "pairing_method": "swiss"}
    )

    # Round 1
    round1 = gen.add_round(tournament, swiss, 1, time_limit_minutes=50, status="completed")
    gen.add_match(tournament, swiss, round1, players[0], players[1], 1, 2, 1, 0, "Great opener!")
    gen.add_match(tournament, swiss, round1, players[2], players[3], 2, 0, 2, 0, "Quick match")
    gen.add_match(tournament, swiss, round1, players[4], players[5], 3, 2, 0, 0)
    gen.add_match(tournament, swiss, round1, players[6], players[7], 4, 1, 2, 0)

    # Round 2
    round2 = gen.add_round(tournament, swiss, 2, time_limit_minutes=50, status="completed")
    gen.add_match(tournament, swiss, round2, players[0], players[2], 1, 2, 0, 0)  # 2-0 winners paired
    gen.add_match(tournament, swiss, round2, players[4], players[7], 2, 0, 2, 0)  # 2-0 vs 1-2
    gen.add_match(tournament, swiss, round2, players[1], players[6], 3, 2, 1, 0)  # 1-2 players
    gen.add_match(tournament, swiss, round2, players[3], players[5], 4, 1, 0, 2, "Time draw")

    # Round 3 (current)
    round3 = gen.add_round(tournament, swiss, 3, time_limit_minutes=50, status="active")
    # Matches not yet reported

    return gen


def generate_discord_swiss() -> SeedDataGenerator:
    """Generate Discord Monthly Standard Swiss scenario."""
    gen = SeedDataGenerator()

    # Create venues and formats
    discord_server = gen.add_venue(
        "Discord Server",
        description="Online tournament coordination"
    )

    standard_format = gen.add_format(
        "Standard",
        game_system="magic_the_gathering",
        base_format="constructed",
        sub_format="Standard",
        card_pool="Standard",
        match_structure="BO3"
    )

    # Create 16 players
    players = []
    for i in range(16):
        name = f"Player{i+1}"
        discord_id = f"player{i+1}#{1000+i}" if i % 2 == 0 else None
        email = f"player{i+1}@example.com" if i % 3 == 0 else None
        players.append(gen.add_player(name, discord_id, email))

    # Create tournament
    tournament = gen.add_tournament(
        "Monthly Discord Standard Swiss",
        standard_format,
        discord_server,
        players[0],
        status="registration_open",
        description="Month-long Swiss tournament on Discord"
    )

    # Register players (some late entries)
    for i, player in enumerate(players[:14]):
        status = "late_entry" if i >= 12 else "active"
        gen.register_player(tournament, player, i + 1, status)

    # Create Swiss component (4 rounds for 16 players)
    swiss = gen.add_component(
        tournament,
        "swiss",
        "Swiss Rounds",
        1,
        {"rounds": 4, "pairing_method": "swiss"}
    )

    return gen


def generate_lgs_draft() -> SeedDataGenerator:
    """Generate Local Game Store Draft scenario."""
    gen = SeedDataGenerator()

    # Create venues and formats
    lgs = gen.add_venue(
        "Local Game Store",
        address="123 Main St, Anytown USA",
        description="Friday Night Magic venue"
    )

    draft_format = gen.add_format(
        "Draft FIN",
        game_system="magic_the_gathering",
        base_format="limited",
        sub_format="Traditional Draft",
        card_pool="FIN",
        match_structure="BO3"
    )

    # Create 12 players (pod of 8 + 4 extras)
    players = []
    for i in range(12):
        name = f"Drafter{i+1}"
        players.append(gen.add_player(name))

    # Create tournament
    tournament = gen.add_tournament(
        "Friday Night Draft",
        draft_format,
        lgs,
        players[0],
        status="completed",
        description="Weekly draft pod at the LGS"
    )

    # Register first 8 players
    for i, player in enumerate(players[:8]):
        gen.register_player(tournament, player, i + 1)

    # Create Swiss component (3 rounds)
    swiss = gen.add_component(
        tournament,
        "swiss",
        "Swiss Rounds",
        1,
        {"rounds": 3, "pairing_method": "swiss"}
    )

    # Complete all rounds with results
    for round_num in range(1, 4):
        round_obj = gen.add_round(
            tournament, swiss, round_num,
            time_limit_minutes=50, status="completed"
        )

        # Generate some match results
        if round_num == 1:
            gen.add_match(tournament, swiss, round_obj, players[0], players[1], 1, 2, 0)
            gen.add_match(tournament, swiss, round_obj, players[2], players[3], 2, 2, 1)
            gen.add_match(tournament, swiss, round_obj, players[4], players[5], 3, 1, 2)
            gen.add_match(tournament, swiss, round_obj, players[6], players[7], 4, 0, 2)

    return gen


def generate_multi_tcg_formats() -> SeedDataGenerator:
    """Generate multiple TCG formats for testing."""
    gen = SeedDataGenerator()

    # Create venue
    convention = gen.add_venue(
        "Convention Center",
        address="456 Convention Blvd",
        description="Large tournament events"
    )

    # Create formats for different TCGs
    formats = [
        # MTG Formats
        gen.add_format("Pauper", "magic_the_gathering", "constructed", "Pauper", "Pauper"),
        gen.add_format("Modern", "magic_the_gathering", "constructed", "Modern", "Modern"),
        gen.add_format("Draft FIN", "magic_the_gathering", "limited", "Traditional Draft", "FIN"),
        gen.add_format("JumpStart J22", "magic_the_gathering", "special", "JumpStart", "J22"),

        # Other TCGs
        gen.add_format("Pokemon Standard", "pokemon", "constructed", "Standard", "Standard"),
        gen.add_format("Star Wars Standard", "star_wars_unlimited", "constructed", "Standard", "Standard"),
        gen.add_format("NFL Five Draft", "nfl_five", "limited", "Draft", "Current"),
        gen.add_format("Custom TCG", "custom_tcg", "constructed", "Standard", "Standard")
    ]

    # Create some players
    players = [gen.add_player(f"Player{i}") for i in range(5)]

    return gen


def generate_complete_tournament() -> SeedDataGenerator:
    """Generate a complete tournament with full results."""
    gen = SeedDataGenerator()

    # Use kitchen table as base
    gen = generate_kitchen_table_pauper()

    # Complete round 3
    tournament = list(gen.tournaments.values())[0]
    swiss = list(gen.components.values())[0]
    players = list(gen.players.values())

    # Find round 3 and complete it
    round3 = None
    for r in gen.rounds.values():
        if r.round_number == 3:
            round3 = r
            break

    if round3:
        round3.status = "completed"
        gen.add_match(tournament, swiss, round3, players[0], players[4], 1, 2, 0, 0)  # Undefeated match
        gen.add_match(tournament, swiss, round3, players[2], players[7], 2, 2, 1, 0)
        gen.add_match(tournament, swiss, round3, players[1], players[3], 3, 0, 2, 0)
        gen.add_match(tournament, swiss, round3, players[5], players[6], 4, 1, 1, 1, "Draw for top 4")

    # Create Top 4 elimination
    top4 = gen.add_component(
        tournament,
        "single_elimination",
        "Top 4",
        2,
        {"cut_size": 4, "reseed_rounds": True}
    )

    # Semifinals
    semis = gen.add_round(tournament, top4, 1, time_limit_minutes=60, status="completed")
    gen.add_match(tournament, top4, semis, players[0], players[5], 1, 2, 0, 0, "Semifinal 1")
    gen.add_match(tournament, top4, semis, players[2], players[3], 2, 2, 1, 0, "Semifinal 2")

    # Finals
    finals = gen.add_round(tournament, top4, 2, time_limit_minutes=60, status="completed")
    gen.add_match(tournament, top4, finals, players[0], players[2], 1, 2, 1, 0, "Championship match!")

    # Mark tournament complete
    tournament.status = "completed"

    return gen


def generate_all_seed_data() -> SeedDataGenerator:
    """Generate comprehensive seed data combining all scenarios."""
    gen = SeedDataGenerator()

    # Generate all individual scenarios and merge
    scenarios = [
        generate_kitchen_table_pauper(),
        generate_discord_swiss(),
        generate_lgs_draft(),
        generate_multi_tcg_formats(),
    ]

    # Merge all data (simple concatenation approach)
    for scenario in scenarios:
        gen.players.update(scenario.players)
        gen.venues.update(scenario.venues)
        gen.formats.update(scenario.formats)
        gen.tournaments.update(scenario.tournaments)
        gen.registrations.update(scenario.registrations)
        gen.components.update(scenario.components)
        gen.rounds.update(scenario.rounds)
        gen.matches.update(scenario.matches)

    return gen
