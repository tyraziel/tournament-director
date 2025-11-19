"""
Match Management API endpoints.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.data.exceptions import NotFoundError
from src.models.match import Match, MatchResultSubmit

from ..dependencies import DataLayerDep, PaginationDep

router = APIRouter()


@router.get("/tournaments/{tournament_id}/matches", response_model=list[Match])
async def list_matches(
    tournament_id: UUID,
    data_layer: DataLayerDep,
    pagination: PaginationDep,
    round_number: int | None = None
) -> list[Match]:
    """
    List all matches in a tournament.

    Optional query parameter:
    - **round_number**: Filter matches by specific round
    """
    # Verify tournament exists
    try:
        await data_layer.tournaments.get_by_id(tournament_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament {tournament_id} not found"
        ) from None

    # Get matches
    matches = await data_layer.matches.list_by_tournament(tournament_id)

    # Filter by round if specified
    if round_number is not None:
        matches = [m for m in matches if m.round_number == round_number]

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return matches[start:end]


@router.get("/matches/{match_id}", response_model=Match)
async def get_match(
    match_id: UUID,
    data_layer: DataLayerDep
) -> Match:
    """Get a specific match by ID."""
    try:
        return await data_layer.matches.get_by_id(match_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {match_id} not found"
        ) from None


@router.put("/matches/{match_id}/result", response_model=Match)
async def submit_match_result(
    match_id: UUID,
    result: MatchResultSubmit,
    data_layer: DataLayerDep
) -> Match:
    """
    Submit a match result.

    - **winner_id**: UUID of winner (or None for draw)
    - **player1_wins**: Games won by player 1
    - **player2_wins**: Games won by player 2
    - **draws**: Number of drawn games
    - **notes**: Optional notes
    """
    # Get match
    try:
        match = await data_layer.matches.get_by_id(match_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {match_id} not found"
        ) from None

    # Validate winner is one of the players (if not a draw)
    if (
        result.winner_id is not None
        and result.winner_id not in [match.player1_id, match.player2_id]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="winner_id must be either player1_id or player2_id"
        )

    # Update match with result
    match.player1_wins = result.player1_wins
    match.player2_wins = result.player2_wins
    match.draws = result.draws
    match.end_time = datetime.now(timezone.utc)
    if result.notes:
        match.notes = result.notes

    # Save updated match
    return await data_layer.matches.update(match)
