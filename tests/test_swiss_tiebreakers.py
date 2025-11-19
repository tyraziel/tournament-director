"""
Unit tests for Swiss tiebreaker calculations.

Tests individual tiebreaker calculators (MW%, GW%, OMW%, OGW%) with
various scenarios including edge cases.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import pytest
from uuid import uuid4

from src.models.player import Player
from src.models.tournament import TournamentRegistration
from src.models.match import Match
from src.models.base import PlayerStatus
from src.swiss.tiebreakers import (
    calculate_match_win_percentage,
    calculate_game_win_percentage,
    calculate_opponent_match_win_percentage,
    calculate_opponent_game_win_percentage,
)


@pytest.fixture
def base_tournament_data():
    """Create basic tournament data for testing."""
    tournament_id = uuid4()
    component_id = uuid4()
    round_id = uuid4()

    return {
        "tournament_id": tournament_id,
        "component_id": component_id,
        "round_id": round_id,
    }


# ===== Match Win Percentage (MW%) Tests =====


def test_mw_perfect_record(base_tournament_data):
    """Test MW% for player with 3-0 record."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    opponent1 = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=2,
        status=PlayerStatus.ACTIVE,
    )

    opponent2 = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=3,
        status=PlayerStatus.ACTIVE,
    )

    opponent3 = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=4,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=opponent1.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=opponent2.player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=3,
            player1_id=player.player_id,
            player2_id=opponent3.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    all_registrations = [player, opponent1, opponent2, opponent3]
    config = {"mw_floor": 0.33}

    mw_pct = calculate_match_win_percentage(player, matches, all_registrations, config)

    # 3 wins, 0 losses = 3/3 = 100%
    assert mw_pct == pytest.approx(1.0, abs=0.01)


def test_mw_losing_record(base_tournament_data):
    """Test MW% for player with 1-2 record."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Win
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=0,
        ),
        # Loss
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=0,
            player2_wins=2,
        ),
        # Loss
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=3,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=1,
            player2_wins=2,
        ),
    ]

    config = {"mw_floor": 0.33}

    mw_pct = calculate_match_win_percentage(player, matches, [], config)

    # 1 win, 2 losses = 1/3 = 33.33%
    assert mw_pct == pytest.approx(0.3333, abs=0.01)


def test_mw_floor_application(base_tournament_data):
    """Test that MW% floor (33.33%) is applied for 0-3 record."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Three losses
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=0,
            player2_wins=2,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=0,
            player2_wins=2,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=3,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=1,
            player2_wins=2,
        ),
    ]

    config = {"mw_floor": 0.33}

    mw_pct = calculate_match_win_percentage(player, matches, [], config)

    # 0 wins, 3 losses = 0/3 = 0%, but floor at 33.33%
    assert mw_pct == pytest.approx(0.33, abs=0.01)


def test_mw_with_draws(base_tournament_data):
    """Test MW% calculation with draws (draws count as 0.5 wins)."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Win
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=0,
            draws=0,
        ),
        # Draw (1-1-1 in games)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=1,
            player2_wins=1,
            draws=1,
        ),
        # Loss
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=3,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=0,
            player2_wins=2,
            draws=0,
        ),
    ]

    config = {"mw_floor": 0.33}

    mw_pct = calculate_match_win_percentage(player, matches, [], config)

    # 1 win + 0.5 draw = 1.5 wins out of 3 matches = 50%
    assert mw_pct == pytest.approx(0.50, abs=0.01)


def test_mw_bye_counts_as_win(base_tournament_data):
    """Test that bye (player2_id=None) counts as a win."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Bye (counts as win)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=None,  # Bye
            player1_wins=2,
            player2_wins=0,
        ),
        # Actual win
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    config = {"mw_floor": 0.33}

    mw_pct = calculate_match_win_percentage(player, matches, [], config)

    # 2 wins (including bye) out of 2 matches = 100%
    assert mw_pct == pytest.approx(1.0, abs=0.01)


# ===== Game Win Percentage (GW%) Tests =====


def test_gw_perfect_games(base_tournament_data):
    """Test GW% for player who won all games."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    config = {"gw_floor": 0.33}

    gw_pct = calculate_game_win_percentage(player, matches, [], config)

    # 4 game wins, 0 losses = 4/4 = 100%
    assert gw_pct == pytest.approx(1.0, abs=0.01)


def test_gw_mixed_results(base_tournament_data):
    """Test GW% with mixed game results."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Win 2-0
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=0,
        ),
        # Win 2-1 (close match)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=1,
        ),
        # Loss 1-2
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=3,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=1,
            player2_wins=2,
        ),
    ]

    config = {"gw_floor": 0.33}

    gw_pct = calculate_game_win_percentage(player, matches, [], config)

    # 5 game wins, 3 game losses = 5/8 = 62.5%
    assert gw_pct == pytest.approx(0.625, abs=0.01)


def test_gw_floor_application(base_tournament_data):
    """Test GW% floor is applied correctly."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # 0-2 loss
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=0,
            player2_wins=2,
        ),
        # 0-2 loss
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=0,
            player2_wins=2,
        ),
    ]

    config = {"gw_floor": 0.33}

    gw_pct = calculate_game_win_percentage(player, matches, [], config)

    # 0 game wins, 4 game losses = 0/4 = 0%, but floor at 33%
    assert gw_pct == pytest.approx(0.33, abs=0.01)


def test_gw_bye_included(base_tournament_data):
    """Test that bye games are included in GW% calculation."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Bye (2-0 in games)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=1,
            player1_id=player.player_id,
            player2_id=None,  # Bye
            player1_wins=2,
            player2_wins=0,
        ),
        # Win 2-1
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=base_tournament_data["round_id"],
            round_number=2,
            player1_id=player.player_id,
            player2_id=uuid4(),
            player1_wins=2,
            player2_wins=1,
        ),
    ]

    config = {"gw_floor": 0.33}

    gw_pct = calculate_game_win_percentage(player, matches, [], config)

    # 4 game wins (2 from bye, 2 from match), 1 game loss = 4/5 = 80%
    assert gw_pct == pytest.approx(0.80, abs=0.01)


# ===== Opponent Match Win % (OMW%) Tests =====


def test_omw_simple_case(base_tournament_data):
    """Test OMW% with simple opponent records."""
    # Player A beat B and C
    # B went 1-2 overall (33.33% MW)
    # C went 2-1 overall (66.67% MW)
    # OMW% = (33.33 + 66.67) / 2 = 50%

    player_a = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    player_b = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=2,
        status=PlayerStatus.ACTIVE,
    )

    player_c = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=3,
        status=PlayerStatus.ACTIVE,
    )

    player_d = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=4,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Round 1: A beats B, C beats D
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=1,
            player1_id=player_a.player_id,
            player2_id=player_b.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=1,
            player1_id=player_c.player_id,
            player2_id=player_d.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        # Round 2: A beats C, D beats B
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=2,
            player1_id=player_a.player_id,
            player2_id=player_c.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=2,
            player1_id=player_d.player_id,
            player2_id=player_b.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        # Round 3: A beats D, C beats B
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=3,
            player1_id=player_a.player_id,
            player2_id=player_d.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=3,
            player1_id=player_c.player_id,
            player2_id=player_b.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    all_registrations = [player_a, player_b, player_c, player_d]
    config = {"omw_floor": 0.33}

    # Player A's opponents: B (0-3 = 0% → 33% floor), C (2-1 = 66.67%), D (1-2 = 33%)
    omw_pct = calculate_opponent_match_win_percentage(
        player_a, matches, all_registrations, config
    )

    # (33 + 66.67 + 33) / 3 = 44.22%
    assert omw_pct == pytest.approx(0.4422, abs=0.01)


def test_omw_excludes_byes(base_tournament_data):
    """Test that byes are excluded from OMW% calculation."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    opponent = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=2,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Player gets bye (should NOT count toward OMW%)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=1,
            player1_id=player.player_id,
            player2_id=None,  # Bye
            player1_wins=2,
            player2_wins=0,
        ),
        # Player beats opponent (opponent went 0-1 = 0% → 33% floor)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=2,
            player1_id=player.player_id,
            player2_id=opponent.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    all_registrations = [player, opponent]
    config = {"omw_floor": 0.33}

    omw_pct = calculate_opponent_match_win_percentage(
        player, matches, all_registrations, config
    )

    # Only 1 opponent (not bye): opponent at 0-1 = 33% (floor)
    # OMW% = 33%
    assert omw_pct == pytest.approx(0.33, abs=0.01)


def test_omw_zero_opponents(base_tournament_data):
    """Test OMW% when player only had byes (no opponents)."""
    player = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # Only byes
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=1,
            player1_id=player.player_id,
            player2_id=None,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=2,
            player1_id=player.player_id,
            player2_id=None,
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    config = {"omw_floor": 0.33}

    omw_pct = calculate_opponent_match_win_percentage(player, matches, [], config)

    # No opponents = 0.0% OMW
    assert omw_pct == 0.0


# ===== Opponent Game Win % (OGW%) Tests =====


def test_ogw_simple_case(base_tournament_data):
    """Test OGW% calculation."""
    # Similar to OMW% test but using game win percentages

    player_a = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
    )

    player_b = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=2,
        status=PlayerStatus.ACTIVE,
    )

    player_c = TournamentRegistration(
        id=uuid4(),
        tournament_id=base_tournament_data["tournament_id"],
        player_id=uuid4(),
        sequence_id=3,
        status=PlayerStatus.ACTIVE,
    )

    matches = [
        # A beats B (2-0)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=1,
            player1_id=player_a.player_id,
            player2_id=player_b.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        # A beats C (2-1)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=2,
            player1_id=player_a.player_id,
            player2_id=player_c.player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        # B beats C (2-0)
        Match(
            id=uuid4(),
            tournament_id=base_tournament_data["tournament_id"],
            component_id=base_tournament_data["component_id"],
            round_id=uuid4(),
            round_number=3,
            player1_id=player_b.player_id,
            player2_id=player_c.player_id,
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    all_registrations = [player_a, player_b, player_c]
    config = {"gw_floor": 0.33, "omw_floor": 0.33}

    # Player A's opponents:
    # - B: 2 game wins, 2 game losses = 2/4 = 50% GW
    # - C: 1 game win, 4 game losses = 1/5 = 20% → 33% floor
    # OGW% = (50 + 33) / 2 = 41.5%

    ogw_pct = calculate_opponent_game_win_percentage(
        player_a, matches, all_registrations, config
    )

    assert ogw_pct == pytest.approx(0.415, abs=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
