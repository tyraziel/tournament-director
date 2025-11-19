"""
Tournament lifecycle management tests.

Tests for round advancement, tournament state transitions,
and automated tournament progression.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.models.player import Player
from src.models.tournament import Tournament, TournamentRegistration, RegistrationControl
from src.models.format import Format
from src.models.venue import Venue
from src.models.match import Match, Round, Component
from src.models.base import (
    GameSystem,
    BaseFormat,
    TournamentStatus,
    TournamentVisibility,
    PlayerStatus,
    ComponentType,
    ComponentStatus,
    RoundStatus,
)


class TestRoundAdvancement:
    """Test round advancement logic."""

    def test_detect_round_completion(self):
        """
        SCENARIO: All matches in a round have results
        EXPECTED: Round should be detected as complete
        """
        # Create round with 4 matches
        round_id = uuid4()
        tournament_id = uuid4()
        component_id = uuid4()

        round_obj = Round(
            id=round_id,
            tournament_id=tournament_id,
            component_id=component_id,
            round_number=1,
            status=RoundStatus.ACTIVE,
        )

        matches = [
            Match(
                id=uuid4(),
                tournament_id=tournament_id,
                component_id=component_id,
                round_id=round_id,
                round_number=1,
                player1_id=uuid4(),
                player2_id=uuid4(),
                player1_wins=2,
                player2_wins=0,
                end_time=datetime.now(timezone.utc),  # Match is complete
                table_number=i + 1,
            )
            for i in range(4)
        ]

        # Test round completion detection
        from src.lifecycle import is_round_complete

        assert is_round_complete(round_obj, matches) is True

    def test_detect_round_incomplete(self):
        """
        SCENARIO: Some matches in a round don't have results
        EXPECTED: Round should be detected as incomplete
        """
        round_id = uuid4()
        tournament_id = uuid4()
        component_id = uuid4()

        round_obj = Round(
            id=round_id,
            tournament_id=tournament_id,
            component_id=component_id,
            round_number=1,
            status=RoundStatus.ACTIVE,
        )

        matches = [
            Match(
                id=uuid4(),
                tournament_id=tournament_id,
                component_id=component_id,
                round_id=round_id,
                round_number=1,
                player1_id=uuid4(),
                player2_id=uuid4(),
                player1_wins=2,
                player2_wins=0,
                end_time=datetime.now(timezone.utc) if i < 2 else None,  # Last 2 incomplete
                table_number=i + 1,
            )
            for i in range(4)
        ]

        from src.lifecycle import is_round_complete

        assert is_round_complete(round_obj, matches) is False

    def test_advance_to_next_round(self):
        """
        SCENARIO: Round 1 complete, advance to Round 2
        EXPECTED: Create Round 2 with ACTIVE status, Round 1 marked COMPLETED
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        from src.lifecycle import advance_to_next_round

        tournament_id = uuid4()
        component_id = uuid4()

        # Round 1 is currently active
        round1 = Round(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_number=1,
            status=RoundStatus.ACTIVE,
            start_time=datetime.now(timezone.utc),
        )

        # Advance to round 2
        round2 = advance_to_next_round(round1, component_id, tournament_id, max_rounds=3)

        # Verify Round 1 was marked complete
        assert round1.status == RoundStatus.COMPLETED
        assert round1.end_time is not None

        # Verify Round 2 was created
        assert round2 is not None
        assert round2.round_number == 2
        assert round2.status == RoundStatus.ACTIVE
        assert round2.tournament_id == tournament_id
        assert round2.component_id == component_id
        assert round2.start_time is not None
        assert round2.end_time is None

    def test_advance_stops_at_max_rounds(self):
        """
        SCENARIO: Tournament has max_rounds=3, currently on Round 3
        EXPECTED: advance_to_next_round returns None (tournament complete)
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        from src.lifecycle import advance_to_next_round

        tournament_id = uuid4()
        component_id = uuid4()

        # Round 3 is the final round
        round3 = Round(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_number=3,
            status=RoundStatus.ACTIVE,
            start_time=datetime.now(timezone.utc),
        )

        # Try to advance past max rounds
        round4 = advance_to_next_round(round3, component_id, tournament_id, max_rounds=3)

        # Verify Round 3 was marked complete
        assert round3.status == RoundStatus.COMPLETED
        assert round3.end_time is not None

        # Verify no Round 4 created (tournament ended)
        assert round4 is None

    def test_should_tournament_end(self):
        """
        SCENARIO: Check various tournament end conditions
        EXPECTED: Correctly identify when tournament should end
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
        from src.lifecycle import should_tournament_end

        tournament_id = uuid4()
        component_id = uuid4()

        # Case 1: Reached max rounds
        rounds = [
            Round(
                id=uuid4(),
                tournament_id=tournament_id,
                component_id=component_id,
                round_number=i,
                status=RoundStatus.COMPLETED,
            )
            for i in range(1, 4)  # 3 rounds completed
        ]
        matches = []

        assert should_tournament_end(rounds, matches, max_rounds=3) is True

        # Case 2: Haven't reached max rounds
        assert should_tournament_end(rounds, matches, max_rounds=5) is False

        # Case 3: No rounds yet
        assert should_tournament_end([], [], max_rounds=3) is False

        # Case 4: Below minimum rounds
        assert should_tournament_end(rounds[:1], matches, min_rounds=3) is False


class TestTournamentStateMachine:
    """Test tournament state transitions."""

    def test_start_tournament_from_draft(self):
        """
        SCENARIO: Tournament in DRAFT status, TO clicks "Start Tournament"
        EXPECTED: Status changes to IN_PROGRESS, Round 1 created with pairings
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - TDD RED phase
        from src.lifecycle import start_tournament

        # Create tournament in DRAFT status
        tournament_id = uuid4()
        venue_id = uuid4()
        format_id = uuid4()
        to_id = uuid4()

        tournament = Tournament(
            id=tournament_id,
            name="Friday Night Pauper",
            status=TournamentStatus.DRAFT,
            registration=RegistrationControl(),
            format_id=format_id,
            venue_id=venue_id,
            created_by=to_id,
        )

        # Create Swiss component
        component_id = uuid4()
        component = Component(
            id=component_id,
            tournament_id=tournament_id,
            type=ComponentType.SWISS,
            name="Swiss Rounds",
            sequence_order=1,
            status=ComponentStatus.PENDING,
            config={"max_rounds": 3},
        )

        # Create 8 registered players
        registrations = [
            TournamentRegistration(
                id=uuid4(),
                tournament_id=tournament_id,
                player_id=uuid4(),
                sequence_id=i + 1,
                status=PlayerStatus.ACTIVE,
            )
            for i in range(8)
        ]

        # Start tournament
        round1 = start_tournament(tournament, component, registrations)

        # Verify tournament state changed
        assert tournament.status == TournamentStatus.IN_PROGRESS
        assert tournament.start_time is not None

        # Verify component activated
        assert component.status == ComponentStatus.ACTIVE

        # Verify Round 1 created
        assert round1 is not None
        assert round1.round_number == 1
        assert round1.status == RoundStatus.ACTIVE
        assert round1.tournament_id == tournament_id
        assert round1.component_id == component_id

    def test_start_tournament_requires_minimum_players(self):
        """
        SCENARIO: Try to start tournament with 0 or 1 player
        EXPECTED: Raise ValueError with helpful message
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - TDD RED phase
        from src.lifecycle import start_tournament

        tournament_id = uuid4()
        tournament = Tournament(
            id=tournament_id,
            name="Empty Tournament",
            status=TournamentStatus.DRAFT,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
        )

        component = Component(
            id=uuid4(),
            tournament_id=tournament_id,
            type=ComponentType.SWISS,
            name="Swiss Rounds",
            sequence_order=1,
            status=ComponentStatus.PENDING,
            config={"max_rounds": 3},
        )

        # Case 1: No players
        with pytest.raises(ValueError, match="at least 2 players"):
            start_tournament(tournament, component, [])

        # Case 2: Only 1 player
        one_player = [
            TournamentRegistration(
                id=uuid4(),
                tournament_id=tournament_id,
                player_id=uuid4(),
                sequence_id=1,
                status=PlayerStatus.ACTIVE,
            )
        ]

        with pytest.raises(ValueError, match="at least 2 players"):
            start_tournament(tournament, component, one_player)

    def test_start_tournament_only_from_valid_states(self):
        """
        SCENARIO: Try to start tournament that's already IN_PROGRESS or COMPLETED
        EXPECTED: Raise ValueError indicating invalid state transition
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - TDD RED phase
        from src.lifecycle import start_tournament

        tournament_id = uuid4()
        component = Component(
            id=uuid4(),
            tournament_id=tournament_id,
            type=ComponentType.SWISS,
            name="Swiss Rounds",
            sequence_order=1,
            status=ComponentStatus.ACTIVE,
            config={},
        )

        registrations = [
            TournamentRegistration(
                id=uuid4(),
                tournament_id=tournament_id,
                player_id=uuid4(),
                sequence_id=i + 1,
                status=PlayerStatus.ACTIVE,
            )
            for i in range(4)
        ]

        # Case 1: Already IN_PROGRESS
        tournament_in_progress = Tournament(
            id=tournament_id,
            name="In Progress Tournament",
            status=TournamentStatus.IN_PROGRESS,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
        )

        with pytest.raises(ValueError, match="Cannot start tournament.*in_progress"):
            start_tournament(tournament_in_progress, component, registrations)

        # Case 2: Already COMPLETED
        tournament_completed = Tournament(
            id=tournament_id,
            name="Completed Tournament",
            status=TournamentStatus.COMPLETED,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
        )

        with pytest.raises(ValueError, match="Cannot start tournament.*completed"):
            start_tournament(tournament_completed, component, registrations)

    def test_end_tournament_manual(self):
        """
        SCENARIO: TO manually ends tournament (early termination or final round)
        EXPECTED: Status changes to COMPLETED, end_time set, component completed
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - TDD RED phase
        from src.lifecycle import end_tournament

        tournament_id = uuid4()
        tournament = Tournament(
            id=tournament_id,
            name="Kitchen Table Pauper",
            status=TournamentStatus.IN_PROGRESS,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
            start_time=datetime.now(timezone.utc),
        )

        component = Component(
            id=uuid4(),
            tournament_id=tournament_id,
            type=ComponentType.SWISS,
            name="Swiss Rounds",
            sequence_order=1,
            status=ComponentStatus.ACTIVE,
            config={"max_rounds": 3},
        )

        # End tournament
        end_tournament(tournament, component)

        # Verify tournament completed
        assert tournament.status == TournamentStatus.COMPLETED
        assert tournament.end_time is not None

        # Verify component completed
        assert component.status == ComponentStatus.COMPLETED

    def test_end_tournament_only_from_in_progress(self):
        """
        SCENARIO: Try to end tournament that's DRAFT or already COMPLETED
        EXPECTED: Raise ValueError indicating invalid state
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - TDD RED phase
        from src.lifecycle import end_tournament

        tournament_id = uuid4()
        component = Component(
            id=uuid4(),
            tournament_id=tournament_id,
            type=ComponentType.SWISS,
            name="Swiss Rounds",
            sequence_order=1,
            status=ComponentStatus.PENDING,
            config={},
        )

        # Case 1: Tournament in DRAFT (never started)
        tournament_draft = Tournament(
            id=tournament_id,
            name="Draft Tournament",
            status=TournamentStatus.DRAFT,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
        )

        with pytest.raises(ValueError, match="Cannot end tournament.*draft"):
            end_tournament(tournament_draft, component)

        # Case 2: Tournament already COMPLETED
        tournament_completed = Tournament(
            id=tournament_id,
            name="Completed Tournament",
            status=TournamentStatus.COMPLETED,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
        )

        with pytest.raises(ValueError, match="Cannot end tournament.*completed"):
            end_tournament(tournament_completed, component)

    def test_automatic_tournament_completion_on_max_rounds(self):
        """
        SCENARIO: Round 3 (final round) completes, advance_to_next_round called
        EXPECTED: advance_to_next_round automatically ends tournament, returns None
        """
        # AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - TDD RED phase
        from src.lifecycle import advance_to_next_round

        tournament_id = uuid4()
        component_id = uuid4()

        tournament = Tournament(
            id=tournament_id,
            name="Auto-Complete Tournament",
            status=TournamentStatus.IN_PROGRESS,
            registration=RegistrationControl(),
            format_id=uuid4(),
            venue_id=uuid4(),
            created_by=uuid4(),
            start_time=datetime.now(timezone.utc),
        )

        component = Component(
            id=component_id,
            tournament_id=tournament_id,
            type=ComponentType.SWISS,
            name="Swiss Rounds",
            sequence_order=1,
            status=ComponentStatus.ACTIVE,
            config={"max_rounds": 3},
        )

        # Round 3 just completed
        round3 = Round(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_number=3,
            status=RoundStatus.ACTIVE,
            start_time=datetime.now(timezone.utc),
        )

        # Advance past final round
        round4 = advance_to_next_round(
            round3, component_id, tournament_id, tournament=tournament, component=component, max_rounds=3
        )

        # Verify no next round created
        assert round4 is None

        # Verify Round 3 marked complete
        assert round3.status == RoundStatus.COMPLETED

        # Verify tournament auto-completed
        assert tournament.status == TournamentStatus.COMPLETED
        assert tournament.end_time is not None

        # Verify component auto-completed
        assert component.status == ComponentStatus.COMPLETED
