"""
Swiss tournament tiebreaker calculators.

Implements Match Win %, Game Win %, Opponent Match Win %, and
Opponent Game Win % calculations following MTG DCI Swiss rules.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from uuid import UUID

from src.models.match import Match
from src.models.tournament import TournamentRegistration


def is_bye_match(match: Match) -> bool:
    """Check if a match is a bye (no opponent)."""
    return match.player2_id is None


def get_player_matches(player: TournamentRegistration, matches: list[Match]) -> list[Match]:
    """Get all matches for a specific player."""
    return [
        m for m in matches if m.player1_id == player.player_id or m.player2_id == player.player_id
    ]


def get_match_result_for_player(
    player: TournamentRegistration, match: Match
) -> tuple[int, int, int]:
    """
    Get match result from player's perspective.

    Returns: (wins, losses, draws)
    """
    if is_bye_match(match):
        # Bye counts as a win with configured game wins
        return (1, 0, 0)

    # Determine if player is player1 or player2
    if match.player1_id == player.player_id:
        player_wins = match.player1_wins
        opponent_wins = match.player2_wins
    else:
        player_wins = match.player2_wins
        opponent_wins = match.player1_wins

    # Determine match result
    if player_wins > opponent_wins:
        return (1, 0, 0)  # Win
    if player_wins < opponent_wins:
        return (0, 1, 0)  # Loss
    return (0, 0, 1)  # Draw (equal wins)


def get_game_result_for_player(player: TournamentRegistration, match: Match) -> tuple[int, int]:
    """
    Get game results from player's perspective.

    Returns: (game_wins, game_losses)
    """
    if is_bye_match(match):
        # Bye games count as configured wins
        return (match.player1_wins, 0)

    # Determine if player is player1 or player2
    if match.player1_id == player.player_id:
        return (match.player1_wins, match.player2_wins)
    return (match.player2_wins, match.player1_wins)


def get_opponent_id(player: TournamentRegistration, match: Match) -> UUID | None:
    """Get the opponent's player_id for a match, or None if bye."""
    if is_bye_match(match):
        return None

    if match.player1_id == player.player_id:
        return match.player2_id
    return match.player1_id


def calculate_match_win_percentage(
    player: TournamentRegistration,
    matches: list[Match],
    all_registrations: list[TournamentRegistration],
    config: dict,
) -> float:
    """
    Calculate Match Win Percentage (MW%) for a player.

    MW% = (Match Wins + 0.5 * Draws) / Total Matches
    Minimum floor applied (default 33.33% per MTG rules).

    Args:
        player: The player registration
        matches: All matches in the tournament
        all_registrations: All player registrations (unused here, for API consistency)
        config: Configuration dict with optional "mw_floor" (default 0.33)

    Returns:
        Match win percentage (0.0 to 1.0)
    """
    player_matches = get_player_matches(player, matches)

    if not player_matches:
        return 0.0

    total_wins = 0.0
    total_matches = len(player_matches)

    for match in player_matches:
        wins, losses, draws = get_match_result_for_player(player, match)
        total_wins += wins + (draws * 0.5)  # Draws count as 0.5 wins

    mw_pct = total_wins / total_matches

    # Apply floor
    floor: float = float(config.get("mw_floor", 0.33))
    return max(mw_pct, floor)


def calculate_game_win_percentage(
    player: TournamentRegistration,
    matches: list[Match],
    all_registrations: list[TournamentRegistration],
    config: dict,
) -> float:
    """
    Calculate Game Win Percentage (GW%) for a player.

    GW% = Game Wins / (Game Wins + Game Losses)
    Minimum floor applied (default 33.33% per MTG rules).
    Byes count as game wins.

    Args:
        player: The player registration
        matches: All matches in the tournament
        all_registrations: All player registrations (unused here, for API consistency)
        config: Configuration dict with optional "gw_floor" (default 0.33)

    Returns:
        Game win percentage (0.0 to 1.0)
    """
    player_matches = get_player_matches(player, matches)

    if not player_matches:
        return 0.0

    total_game_wins = 0
    total_game_losses = 0

    for match in player_matches:
        game_wins, game_losses = get_game_result_for_player(player, match)
        total_game_wins += game_wins
        total_game_losses += game_losses

    total_games = total_game_wins + total_game_losses

    if total_games == 0:
        return 0.0

    gw_pct = total_game_wins / total_games

    # Apply floor
    floor: float = float(config.get("gw_floor", 0.33))
    return max(gw_pct, floor)


def calculate_opponent_match_win_percentage(
    player: TournamentRegistration,
    matches: list[Match],
    all_registrations: list[TournamentRegistration],
    config: dict,
) -> float:
    """
    Calculate Opponent Match Win Percentage (OMW%) for a player.

    OMW% = Average of all opponents' match win percentages
    Byes are excluded (no opponent to contribute).
    Floor is applied to each opponent's MW% before averaging.

    Args:
        player: The player registration
        matches: All matches in the tournament
        all_registrations: All player registrations
        config: Configuration dict with "omw_floor" (default 0.33)

    Returns:
        Opponent match win percentage (0.0 to 1.0)
    """
    player_matches = get_player_matches(player, matches)

    # Get list of opponent IDs (excluding byes)
    opponent_ids = []
    for match in player_matches:
        opponent_id = get_opponent_id(player, match)
        if opponent_id is not None:  # Exclude byes
            opponent_ids.append(opponent_id)

    if not opponent_ids:
        return 0.0  # No opponents (only byes)

    # Calculate each opponent's MW%
    opponent_mw_pcts = []

    for opponent_id in opponent_ids:
        # Find opponent registration
        opponent = next((reg for reg in all_registrations if reg.player_id == opponent_id), None)

        if opponent is None:
            continue  # Skip if opponent not found

        # Calculate opponent's MW%
        opponent_mw = calculate_match_win_percentage(opponent, matches, all_registrations, config)
        opponent_mw_pcts.append(opponent_mw)

    if not opponent_mw_pcts:
        return 0.0

    # Return average of opponent MW%
    return sum(opponent_mw_pcts) / len(opponent_mw_pcts)


def calculate_opponent_game_win_percentage(
    player: TournamentRegistration,
    matches: list[Match],
    all_registrations: list[TournamentRegistration],
    config: dict,
) -> float:
    """
    Calculate Opponent Game Win Percentage (OGW%) for a player.

    OGW% = Average of all opponents' game win percentages
    Byes are excluded (no opponent to contribute).
    Floor is applied to each opponent's GW% before averaging.

    Args:
        player: The player registration
        matches: All matches in the tournament
        all_registrations: All player registrations
        config: Configuration dict with "gw_floor" (default 0.33)

    Returns:
        Opponent game win percentage (0.0 to 1.0)
    """
    player_matches = get_player_matches(player, matches)

    # Get list of opponent IDs (excluding byes)
    opponent_ids = []
    for match in player_matches:
        opponent_id = get_opponent_id(player, match)
        if opponent_id is not None:  # Exclude byes
            opponent_ids.append(opponent_id)

    if not opponent_ids:
        return 0.0  # No opponents (only byes)

    # Calculate each opponent's GW%
    opponent_gw_pcts = []

    for opponent_id in opponent_ids:
        # Find opponent registration
        opponent = next((reg for reg in all_registrations if reg.player_id == opponent_id), None)

        if opponent is None:
            continue  # Skip if opponent not found

        # Calculate opponent's GW%
        opponent_gw = calculate_game_win_percentage(opponent, matches, all_registrations, config)
        opponent_gw_pcts.append(opponent_gw)

    if not opponent_gw_pcts:
        return 0.0

    # Return average of opponent GW%
    return sum(opponent_gw_pcts) / len(opponent_gw_pcts)
