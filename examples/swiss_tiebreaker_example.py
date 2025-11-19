"""
Example tournament demonstrating Swiss tiebreaker calculations.

This example shows how OMW%, GW%, and OGW% tiebreakers work in practice
with a 6-player, 3-round Swiss tournament.

Run with: python3 examples/swiss_tiebreaker_example.py

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import uuid4

from src.models.tournament import TournamentRegistration
from src.models.match import Match
from src.models.base import PlayerStatus
from src.swiss.tiebreakers import (
    calculate_match_win_percentage,
    calculate_game_win_percentage,
    calculate_opponent_match_win_percentage,
    calculate_opponent_game_win_percentage,
)


def create_tiebreaker_triangle_tournament():
    """
    Create a tournament that demonstrates tiebreaker importance.

    Tournament Structure:
    - 6 players (Alice, Bob, Carol, David, Eve, Frank)
    - 3 rounds of Swiss
    - Final standings: Alice, Bob, Carol all finish 2-1 (6 points)
    - Tiebreakers determine final order!

    Results:
    Round 1:
    - Alice def. David (2-1) - Close match
    - Bob def. Eve (2-0) - Dominant
    - Carol def. Frank (2-0) - Dominant

    Round 2:
    - Alice def. Bob (2-1) - Close match
    - Carol def. David (2-0) - Dominant
    - Eve def. Frank (2-1) - Close match

    Round 3:
    - Bob def. Carol (2-1) - Close match
    - David def. Alice (2-1) - Upset!
    - Eve def. Frank (2-0) - Dominant

    Final Records:
    - Alice: 2-1 (beat David, Bob; lost to David)
    - Bob: 2-1 (beat Eve, Carol; lost to Alice)
    - Carol: 2-1 (beat Frank, David; lost to Bob)
    - David: 1-2 (lost to Alice, Carol; beat Alice)
    - Eve: 1-2 (lost to Bob; beat Frank twice)
    - Frank: 0-3 (lost to all)
    """
    tournament_id = uuid4()
    component_id = uuid4()

    # Create player registrations
    players = {
        "Alice": TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament_id,
            player_id=uuid4(),
            sequence_id=1,
            status=PlayerStatus.ACTIVE,
        ),
        "Bob": TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament_id,
            player_id=uuid4(),
            sequence_id=2,
            status=PlayerStatus.ACTIVE,
        ),
        "Carol": TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament_id,
            player_id=uuid4(),
            sequence_id=3,
            status=PlayerStatus.ACTIVE,
        ),
        "David": TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament_id,
            player_id=uuid4(),
            sequence_id=4,
            status=PlayerStatus.ACTIVE,
        ),
        "Eve": TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament_id,
            player_id=uuid4(),
            sequence_id=5,
            status=PlayerStatus.ACTIVE,
        ),
        "Frank": TournamentRegistration(
            id=uuid4(),
            tournament_id=tournament_id,
            player_id=uuid4(),
            sequence_id=6,
            status=PlayerStatus.ACTIVE,
        ),
    }

    # Create matches
    matches = [
        # Round 1
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=1,
            table_number=1,
            player1_id=players["Alice"].player_id,
            player2_id=players["David"].player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=1,
            table_number=2,
            player1_id=players["Bob"].player_id,
            player2_id=players["Eve"].player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=1,
            table_number=3,
            player1_id=players["Carol"].player_id,
            player2_id=players["Frank"].player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        # Round 2
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=2,
            table_number=1,
            player1_id=players["Alice"].player_id,
            player2_id=players["Bob"].player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=2,
            table_number=2,
            player1_id=players["Carol"].player_id,
            player2_id=players["David"].player_id,
            player1_wins=2,
            player2_wins=0,
        ),
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=2,
            table_number=3,
            player1_id=players["Eve"].player_id,
            player2_id=players["Frank"].player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        # Round 3
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=3,
            table_number=1,
            player1_id=players["Bob"].player_id,
            player2_id=players["Carol"].player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=3,
            table_number=2,
            player1_id=players["David"].player_id,
            player2_id=players["Alice"].player_id,
            player1_wins=2,
            player2_wins=1,
        ),
        Match(
            id=uuid4(),
            tournament_id=tournament_id,
            component_id=component_id,
            round_id=uuid4(),
            round_number=3,
            table_number=3,
            player1_id=players["Eve"].player_id,
            player2_id=players["Frank"].player_id,
            player1_wins=2,
            player2_wins=0,
        ),
    ]

    return players, matches


def calculate_all_tiebreakers(player, matches, all_registrations, config):
    """Calculate all tiebreakers for a player."""
    mw = calculate_match_win_percentage(player, matches, all_registrations, config)
    gw = calculate_game_win_percentage(player, matches, all_registrations, config)
    omw = calculate_opponent_match_win_percentage(
        player, matches, all_registrations, config
    )
    ogw = calculate_opponent_game_win_percentage(
        player, matches, all_registrations, config
    )

    return {
        "mw": mw,
        "gw": gw,
        "omw": omw,
        "ogw": ogw,
    }


def count_record(player, matches):
    """Count wins-losses-draws for a player."""
    from src.swiss.tiebreakers import get_player_matches, get_match_result_for_player

    player_matches = get_player_matches(player, matches)
    wins = losses = draws = 0

    for match in player_matches:
        w, l, d = get_match_result_for_player(player, match)
        wins += w
        losses += l
        draws += d

    return wins, losses, draws


def main():
    """Run the tiebreaker example."""
    print("=" * 70)
    print("Swiss Tiebreaker Example: The Tiebreaker Triangle")
    print("=" * 70)
    print()

    # Create tournament
    players, matches = create_tiebreaker_triangle_tournament()
    all_registrations = list(players.values())

    # Configuration (MTG standard)
    config = {
        "mw_floor": 0.33,
        "gw_floor": 0.33,
        "omw_floor": 0.33,
    }

    print("Tournament: 6 players, 3 rounds of Swiss\n")

    # Calculate tiebreakers for all players
    results = {}
    for name, player in players.items():
        wins, losses, draws = count_record(player, matches)
        match_points = (wins * 3) + (draws * 1)
        tiebreakers = calculate_all_tiebreakers(
            player, matches, all_registrations, config
        )

        results[name] = {
            "player": player,
            "record": (wins, losses, draws),
            "match_points": match_points,
            "tiebreakers": tiebreakers,
        }

    # Print standings
    print("FINAL STANDINGS")
    print("-" * 70)
    print(f"{'Rank':<6} {'Player':<10} {'Record':<10} {'Points':<8} {'MW%':<8} {'GW%':<8} {'OMW%':<8} {'OGW%':<8}")
    print("-" * 70)

    # Sort by match points, then OMW%, then GW%, then OGW%
    sorted_results = sorted(
        results.items(),
        key=lambda x: (
            x[1]["match_points"],
            x[1]["tiebreakers"]["omw"],
            x[1]["tiebreakers"]["gw"],
            x[1]["tiebreakers"]["ogw"],
        ),
        reverse=True,
    )

    for rank, (name, data) in enumerate(sorted_results, start=1):
        record = data["record"]
        record_str = f"{record[0]}-{record[1]}-{record[2]}"
        points = data["match_points"]
        tb = data["tiebreakers"]

        print(
            f"{rank:<6} {name:<10} {record_str:<10} {points:<8} "
            f"{tb['mw']*100:>6.2f}% {tb['gw']*100:>6.2f}% "
            f"{tb['omw']*100:>6.2f}% {tb['ogw']*100:>6.2f}%"
        )

    # Highlight the tiebreaker triangle
    print()
    print("=" * 70)
    print("THE TIEBREAKER TRIANGLE: Three 2-1 Players")
    print("=" * 70)
    print()

    print("Alice, Bob, and Carol all finished 2-1 (6 match points).")
    print("Tiebreakers determine their final order:\n")

    for name in ["Alice", "Bob", "Carol"]:
        data = results[name]
        tb = data["tiebreakers"]
        print(f"{name}:")
        print(f"  - MW%:  {tb['mw']*100:.2f}% (all tied at 66.67%)")
        print(f"  - GW%:  {tb['gw']*100:.2f}%")
        print(f"  - OMW%: {tb['omw']*100:.2f}%  ⭐ PRIMARY TIEBREAKER")
        print(f"  - OGW%: {tb['ogw']*100:.2f}%")
        print()

    print("With OMW% as primary tiebreaker:")
    top_three = sorted_results[:3]
    for rank, (name, _) in enumerate(top_three, start=1):
        print(f"  {rank}. {name}")

    print()
    print("=" * 70)
    print("WHAT IF WE USED GW% AS PRIMARY TIEBREAKER?")
    print("=" * 70)
    print()

    # Sort by GW% instead
    gw_sorted = sorted(
        [(n, d) for n, d in results.items() if d["match_points"] == 6],
        key=lambda x: (x[1]["tiebreakers"]["gw"], x[1]["tiebreakers"]["omw"]),
        reverse=True,
    )

    print("New rankings for 2-1 players:")
    for rank, (name, data) in enumerate(gw_sorted, start=1):
        tb = data["tiebreakers"]
        print(f"  {rank}. {name} (GW%: {tb['gw']*100:.2f}%, OMW%: {tb['omw']*100:.2f}%)")

    print()
    print("🎯 Tiebreaker order MATTERS! Different configs = different results!")
    print()


if __name__ == "__main__":
    main()
