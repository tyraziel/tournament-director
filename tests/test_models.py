"""Test suite for Tournament Director data models.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.models.format import Format
from src.models.match import Component, Match, Round
from src.models.player import Player
from src.models.tournament import RegistrationControl, Tournament, TournamentRegistration
from src.models.venue import Venue

from .fixtures import (
    generate_uuid,
)


class TestPlayer:
    """Test Player model validation and behavior."""

    def test_player_creation_valid(self, player_test_cases):
        """Test creating players with valid data."""
        for case in player_test_cases:
            player = Player(
                id=generate_uuid(),
                name=case["name"],
                discord_id=case["discord_id"],
                email=case["email"],
            )
            assert player.name == case["name"]
            assert player.discord_id == case["discord_id"]
            assert player.email == case["email"]
            assert isinstance(player.id, UUID)
            assert isinstance(player.created_at, datetime)

    def test_player_creation_minimal(self):
        """Test creating player with minimal required data."""
        player = Player(id=generate_uuid(), name="Test Player")
        assert player.name == "Test Player"
        assert player.discord_id is None
        assert player.email is None

    def test_player_validation_failures(self):
        """Test player validation edge cases."""
        # Missing required fields should fail
        with pytest.raises(ValidationError):
            Player(name="No ID")  # Missing id

        with pytest.raises(ValidationError):
            Player(id=generate_uuid())  # Missing name

        # Invalid UUID should fail
        with pytest.raises(ValidationError):
            Player(id="not-a-uuid", name="Invalid ID")


class TestFormat:
    """Test Format model validation and behavior."""

    def test_format_creation_valid(self, format_test_cases):
        """Test creating formats with all our test cases."""
        for case in format_test_cases:
            format_obj = Format(
                id=generate_uuid(),
                name=case["name"],
                game_system=case["game_system"],
                base_format=case["base_format"],
                sub_format=case.get("sub_format"),
                card_pool=case["card_pool"],
                match_structure=case.get("match_structure"),
            )
            assert format_obj.name == case["name"]
            assert format_obj.game_system.value == case["game_system"]
            assert format_obj.base_format.value == case["base_format"]
            assert format_obj.card_pool == case["card_pool"]

    def test_pauper_priority(self, format_test_cases):
        """Test that Pauper formats are properly represented."""
        pauper_formats = [case for case in format_test_cases if "Pauper" in case["name"]]
        assert len(pauper_formats) >= 2  # Regular Pauper and Historic Pauper

        # Check regular Pauper format
        pauper = next(case for case in pauper_formats if case["name"] == "Pauper")
        assert pauper["sub_format"] == "Pauper"
        assert pauper["card_pool"] == "Pauper"

        # Check Historic Pauper format
        historic_pauper = next(case for case in pauper_formats if case["name"] == "Historic Pauper")
        assert historic_pauper["sub_format"] == "Pauper"
        assert historic_pauper["card_pool"] == "Historic"

    def test_multi_game_system_support(self, format_test_cases):
        """Test that all game systems are represented."""
        game_systems = {case["game_system"] for case in format_test_cases}
        expected_systems = {
            "magic_the_gathering",
            "pokemon",
            "star_wars_unlimited",
            "nfl_five",
            "custom_tcg",
        }
        assert game_systems >= expected_systems  # Should have at least these

    def test_format_validation_failures(self):
        """Test format validation edge cases."""
        # Invalid game system
        with pytest.raises(ValidationError):
            Format(
                id=generate_uuid(),
                name="Invalid System",
                game_system="invalid_game",
                base_format="constructed",
                card_pool="Standard",
            )

        # Invalid base format
        with pytest.raises(ValidationError):
            Format(
                id=generate_uuid(),
                name="Invalid Base",
                game_system="magic_the_gathering",
                base_format="invalid_base",
                card_pool="Standard",
            )


class TestVenue:
    """Test Venue model validation and behavior."""

    def test_venue_creation_valid(self, venue_test_cases):
        """Test creating venues with all our test cases."""
        for case in venue_test_cases:
            venue = Venue(
                id=generate_uuid(),
                name=case["name"],
                address=case["address"],
                description=case["description"],
            )
            assert venue.name == case["name"]
            assert venue.address == case["address"]
            assert venue.description == case["description"]

    def test_kitchen_table_venue(self, venue_test_cases):
        """Test that Kitchen Table venue is properly represented."""
        kitchen_table = next(case for case in venue_test_cases if case["name"] == "Kitchen Table")
        assert kitchen_table["address"] is None
        assert "home casual" in kitchen_table["description"].lower()


class TestRegistrationControl:
    """Test RegistrationControl model validation and behavior."""

    def test_registration_control_creation(self, registration_control_test_cases):
        """Test creating registration control with various scenarios."""
        for case in registration_control_test_cases:
            control = RegistrationControl(**case)
            assert control.allow_to_override == case["allow_to_override"]
            assert control.registration_password == case["registration_password"]
            assert control.max_players == case["max_players"]

    def test_password_scenarios(self):
        """Test different password scenarios."""
        # No passwords
        control = RegistrationControl()
        assert control.registration_password is None
        assert control.late_registration_password is None
        assert control.to_override_password is None

        # All passwords set
        control = RegistrationControl(
            registration_password="reg123",
            late_registration_password="late456",
            to_override_password="admin789",
        )
        assert control.registration_password == "reg123"
        assert control.late_registration_password == "late456"
        assert control.to_override_password == "admin789"


class TestTournament:
    """Test Tournament model validation and behavior."""

    def test_tournament_creation_valid(self, tournament_test_cases):
        """Test creating tournaments with valid data."""
        for case in tournament_test_cases:
            tournament = Tournament(
                id=generate_uuid(),
                name=case["name"],
                status=case["status"],
                visibility=case["visibility"],
                registration=RegistrationControl(),
                format_id=generate_uuid(),
                venue_id=generate_uuid(),
                created_by=generate_uuid(),
                description=case["description"],
            )
            assert tournament.name == case["name"]
            assert tournament.status.value == case["status"]
            assert tournament.visibility.value == case["visibility"]
            assert isinstance(tournament.created_at, datetime)

    def test_tournament_kitchen_table_vibes(self):
        """Test kitchen table tournament scenario."""
        tournament = Tournament(
            id=generate_uuid(),
            name="Kitchen Table Pauper Championship",
            status="registration_open",
            visibility="public",
            registration=RegistrationControl(max_players=8),
            format_id=generate_uuid(),  # Would be Pauper format
            venue_id=generate_uuid(),  # Would be Kitchen Table venue
            created_by=generate_uuid(),
            description="Monthly Pauper at the kitchen table",
        )
        assert "Kitchen Table" in tournament.name
        assert "Pauper" in tournament.name
        assert tournament.registration.max_players == 8
        assert tournament.auto_advance_rounds is False  # Default no auto-advance
        assert tournament.registration_deadline is None  # Default no deadline

    def test_tournament_with_auto_scheduling(self):
        """Test tournament with auto-advance and registration deadline."""
        from datetime import datetime, timezone, timedelta
        
        registration_deadline = datetime.now(timezone.utc) + timedelta(days=1)
        
        tournament = Tournament(
            id=generate_uuid(),
            name="Discord Monthly Swiss",
            status="registration_open",
            visibility="public",
            registration=RegistrationControl(max_players=16),
            format_id=generate_uuid(),
            venue_id=generate_uuid(),
            created_by=generate_uuid(),
            description="Month-long tournament with auto-progression",
            registration_deadline=registration_deadline,
            auto_advance_rounds=True,
        )
        
        assert tournament.registration_deadline == registration_deadline
        assert tournament.auto_advance_rounds is True

    def test_tournament_manual_control(self):
        """Test tournament with full manual control (LGS style)."""
        tournament = Tournament(
            id=generate_uuid(),
            name="Friday Night Draft",
            status="in_progress",
            visibility="public",
            registration=RegistrationControl(max_players=8),
            format_id=generate_uuid(),
            venue_id=generate_uuid(),
            created_by=generate_uuid(),
            description="In-person draft with TO control",
            auto_advance_rounds=False,  # Manual round progression
        )
        
        assert tournament.auto_advance_rounds is False
        assert tournament.registration_deadline is None


class TestTournamentRegistration:
    """Test TournamentRegistration model validation and behavior."""

    def test_registration_creation_valid(self):
        """Test creating tournament registrations."""
        registration = TournamentRegistration(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            player_id=generate_uuid(),
            sequence_id=1,
            status="active",
        )
        assert registration.sequence_id == 1
        assert registration.status.value == "active"
        assert isinstance(registration.registration_time, datetime)
        assert registration.drop_time is None

    def test_player_drop_scenario(self):
        """Test player drop workflow."""
        registration = TournamentRegistration(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            player_id=generate_uuid(),
            sequence_id=5,
            status="dropped",
            drop_time=datetime.now(timezone.utc),
        )
        assert registration.status.value == "dropped"
        assert registration.drop_time is not None

    def test_late_entry_scenario(self):
        """Test late entry workflow."""
        registration = TournamentRegistration(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            player_id=generate_uuid(),
            sequence_id=9,
            status="late_entry",
        )
        assert registration.status.value == "late_entry"
        assert registration.sequence_id == 9


class TestMatch:
    """Test Match model validation and behavior."""

    def test_match_creation_valid(self, match_result_test_cases):
        """Test creating matches with various results."""
        for case in match_result_test_cases:
            match = Match(
                id=generate_uuid(),
                tournament_id=generate_uuid(),
                component_id=generate_uuid(),
                round_id=generate_uuid(),
                round_number=1,
                player1_id=generate_uuid(),
                player2_id=generate_uuid(),
                player1_wins=case["player1_wins"],
                player2_wins=case["player2_wins"],
                draws=case["draws"],
            )
            assert match.player1_wins == case["player1_wins"]
            assert match.player2_wins == case["player2_wins"]
            assert match.draws == case["draws"]

    def test_bye_match(self):
        """Test bye match (no opponent)."""
        match = Match(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            component_id=generate_uuid(),
            round_id=generate_uuid(),
            round_number=1,
            player1_id=generate_uuid(),
            player2_id=None,  # Bye - no opponent
            player1_wins=2,
            player2_wins=0,
            draws=0,
        )
        assert match.player2_id is None
        assert match.player1_wins == 2
        assert match.player2_wins == 0

    def test_match_with_draws(self):
        """Test match with draws (time limit scenarios)."""
        match = Match(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            component_id=generate_uuid(),
            round_id=generate_uuid(),
            round_number=3,
            player1_id=generate_uuid(),
            player2_id=generate_uuid(),
            player1_wins=1,
            player2_wins=0,
            draws=2,
            notes="Time called, 1-0-2 result",
        )
        assert match.draws == 2
        assert "Time called" in match.notes


class TestComponent:
    """Test Component model validation and behavior."""

    def test_swiss_component_creation(self):
        """Test creating Swiss component."""
        component = Component(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            type="swiss",
            name="Swiss Rounds",
            sequence_order=1,
            config={"rounds": 4, "pairing_method": "swiss"},
        )
        assert component.type.value == "swiss"
        assert component.name == "Swiss Rounds"
        assert component.config["rounds"] == 4

    def test_elimination_component_creation(self):
        """Test creating elimination component."""
        component = Component(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            type="single_elimination",
            name="Top 8",
            sequence_order=2,
            config={"cut_size": 8, "reseed_rounds": True},
        )
        assert component.type.value == "single_elimination"
        assert component.name == "Top 8"
        assert component.config["cut_size"] == 8


class TestRound:
    """Test Round model validation and behavior."""

    def test_round_creation_valid(self):
        """Test creating rounds with time limits."""
        round_obj = Round(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            component_id=generate_uuid(),
            round_number=1,
            time_limit_minutes=50,
            status="active",
        )
        assert round_obj.round_number == 1
        assert round_obj.time_limit_minutes == 50
        assert round_obj.status.value == "active"

    def test_untimed_round(self):
        """Test round without time limit (Discord style)."""
        round_obj = Round(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            component_id=generate_uuid(),
            round_number=2,
            time_limit_minutes=None,  # No time limit
            status="pending",
        )
        assert round_obj.time_limit_minutes is None
        assert round_obj.status.value == "pending"

    def test_scheduled_round(self):
        """Test round with scheduling information."""
        from datetime import datetime, timezone, timedelta
        
        now = datetime.now(timezone.utc)
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=50)
        
        round_obj = Round(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            component_id=generate_uuid(),
            round_number=1,
            time_limit_minutes=50,
            scheduled_start=start_time,
            scheduled_end=end_time,
            auto_advance=True,
            status="pending",
        )
        
        assert round_obj.scheduled_start == start_time
        assert round_obj.scheduled_end == end_time
        assert round_obj.auto_advance is True
        assert round_obj.status.value == "pending"

    def test_manual_round_no_auto_advance(self):
        """Test round without auto-advance (manual TO control)."""
        round_obj = Round(
            id=generate_uuid(),
            tournament_id=generate_uuid(),
            component_id=generate_uuid(),
            round_number=3,
            time_limit_minutes=50,
            auto_advance=False,  # Manual control
            status="active",
        )
        
        assert round_obj.auto_advance is False
        assert round_obj.scheduled_start is None
        assert round_obj.scheduled_end is None


# Integration tests
class TestModelIntegration:
    """Test model relationships and integration scenarios."""

    def test_complete_tournament_scenario(self):
        """Test creating a complete tournament with all related objects."""
        # Create base objects
        player1 = Player(id=generate_uuid(), name="Andrew")
        player2 = Player(id=generate_uuid(), name="Bob")

        venue = Venue(id=generate_uuid(), name="Kitchen Table")

        format_obj = Format(
            id=generate_uuid(),
            name="Pauper",
            game_system="magic_the_gathering",
            base_format="constructed",
            sub_format="Pauper",
            card_pool="Pauper",
        )

        # Create tournament
        tournament = Tournament(
            id=generate_uuid(),
            name="Kitchen Table Pauper Championship",
            status="in_progress",
            visibility="public",
            registration=RegistrationControl(max_players=8),
            format_id=format_obj.id,
            venue_id=venue.id,
            created_by=player1.id,
        )

        # Register players
        reg1 = TournamentRegistration(
            id=generate_uuid(),
            tournament_id=tournament.id,
            player_id=player1.id,
            sequence_id=1,
            status="active",
        )

        reg2 = TournamentRegistration(
            id=generate_uuid(),
            tournament_id=tournament.id,
            player_id=player2.id,
            sequence_id=2,
            status="active",
        )

        # Create Swiss component
        swiss_component = Component(
            id=generate_uuid(),
            tournament_id=tournament.id,
            type="swiss",
            name="Swiss Rounds",
            sequence_order=1,
            config={"rounds": 3},
        )

        # Create round
        round1 = Round(
            id=generate_uuid(),
            tournament_id=tournament.id,
            component_id=swiss_component.id,
            round_number=1,
            time_limit_minutes=50,
            status="completed",
        )

        # Create match
        match = Match(
            id=generate_uuid(),
            tournament_id=tournament.id,
            component_id=swiss_component.id,
            round_id=round1.id,
            round_number=1,
            player1_id=player1.id,
            player2_id=player2.id,
            player1_wins=2,
            player2_wins=1,
            draws=0,
            notes="Great game!",
        )

        # Verify relationships
        assert tournament.format_id == format_obj.id
        assert tournament.venue_id == venue.id
        assert reg1.tournament_id == tournament.id
        assert reg2.tournament_id == tournament.id
        assert swiss_component.tournament_id == tournament.id
        assert round1.component_id == swiss_component.id
        assert match.tournament_id == tournament.id
        assert match.player1_id == player1.id
        assert match.player2_id == player2.id

        # Test the vibes - this should represent a real tournament scenario
        assert "Kitchen Table" in tournament.name
        assert "Pauper" in format_obj.name
        assert reg1.sequence_id == 1  # Andrew is player #1
        assert reg2.sequence_id == 2  # Bob is player #2
        assert match.player1_wins == 2  # Andrew won 2-1

    def test_scheduled_tournament_scenario(self):
        """Test tournament with scheduled rounds and auto-progression."""
        from datetime import datetime, timezone, timedelta
        
        # Create a Discord tournament with scheduling
        tournament = Tournament(
            id=generate_uuid(),
            name="Discord Weekly Swiss",
            status="registration_open",
            visibility="public",
            registration=RegistrationControl(max_players=16),
            format_id=generate_uuid(),
            venue_id=generate_uuid(),
            created_by=generate_uuid(),
            registration_deadline=datetime.now(timezone.utc) + timedelta(days=2),
            auto_advance_rounds=True,
        )
        
        # Create Swiss component
        swiss = Component(
            id=generate_uuid(),
            tournament_id=tournament.id,
            type="swiss",
            name="Swiss Rounds",
            sequence_order=1,
            config={"rounds": 4},
        )
        
        # Create scheduled round
        round1_start = datetime.now(timezone.utc) + timedelta(days=3)
        round1_end = round1_start + timedelta(days=2)
        
        round1 = Round(
            id=generate_uuid(),
            tournament_id=tournament.id,
            component_id=swiss.id,
            round_number=1,
            scheduled_start=round1_start,
            scheduled_end=round1_end,
            auto_advance=True,
            status="pending",
        )
        
        # Verify scheduling integration
        assert tournament.auto_advance_rounds is True
        assert tournament.registration_deadline is not None
        assert round1.scheduled_start == round1_start
        assert round1.scheduled_end == round1_end
        assert round1.auto_advance is True
        
    def test_mixed_scheduling_scenario(self):
        """Test tournament with both scheduled and manual rounds."""
        from datetime import datetime, timezone, timedelta
        
        # Tournament allows auto-advance but some rounds are manual
        tournament = Tournament(
            id=generate_uuid(),
            name="Hybrid Tournament",
            status="in_progress",
            visibility="public",
            registration=RegistrationControl(),
            format_id=generate_uuid(),
            venue_id=generate_uuid(),
            created_by=generate_uuid(),
            auto_advance_rounds=True,  # Global setting
        )
        
        component = Component(
            id=generate_uuid(),
            tournament_id=tournament.id,
            type="swiss",
            name="Swiss",
            sequence_order=1,
        )
        
        # Scheduled round (follows tournament setting)
        scheduled_round = Round(
            id=generate_uuid(),
            tournament_id=tournament.id,
            component_id=component.id,
            round_number=1,
            scheduled_start=datetime.now(timezone.utc) + timedelta(hours=1),
            scheduled_end=datetime.now(timezone.utc) + timedelta(hours=2),
            auto_advance=True,
            status="pending",
        )
        
        # Manual round (overrides tournament setting)
        manual_round = Round(
            id=generate_uuid(),
            tournament_id=tournament.id,
            component_id=component.id,
            round_number=2,
            auto_advance=False,  # Manual override
            status="pending",
        )
        
        # Verify mixed behavior
        assert tournament.auto_advance_rounds is True
        assert scheduled_round.auto_advance is True
        assert scheduled_round.scheduled_start is not None
        assert manual_round.auto_advance is False
        assert manual_round.scheduled_start is None
