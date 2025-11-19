"""
Registration API endpoints for tournament player management.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from src.data.exceptions import NotFoundError
from src.models.base import PlayerStatus
from src.models.tournament import (
    PlayerRegistrationCreate,
    TournamentRegistration,
)

from ..dependencies import DataLayerDep, PaginationDep

router = APIRouter(prefix="/tournaments")


@router.post(
    "/{tournament_id}/register",
    response_model=TournamentRegistration,
    status_code=status.HTTP_201_CREATED,
)
async def register_player(
    tournament_id: UUID, registration_data: PlayerRegistrationCreate, data_layer: DataLayerDep
) -> TournamentRegistration:
    """
    Register a player to a tournament.

    - **player_id**: UUID of the player to register
    - **password**: Optional password for password-protected tournaments
    - **notes**: Optional registration notes

    Business logic:
    - Validates tournament exists
    - Validates player exists
    - Checks for duplicate registration
    - Validates password if tournament requires it
    - Checks max_players limit
    - Assigns sequential player number (sequence_id)
    """
    # Verify tournament exists
    try:
        tournament = await data_layer.tournaments.get_by_id(tournament_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament {tournament_id} not found"
        ) from None

    # Verify player exists
    try:
        await data_layer.players.get_by_id(registration_data.player_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {registration_data.player_id} not found",
        ) from None

    # Check for duplicate registration
    existing_registration = await data_layer.registrations.get_by_tournament_and_player(
        tournament_id, registration_data.player_id
    )
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Player {registration_data.player_id} is already "
                "registered for this tournament"
            ),
        )

    # Validate password if required
    if tournament.registration.registration_password:
        if not registration_data.password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Password required for this tournament",
            )
        if registration_data.password != tournament.registration.registration_password:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    # Check max_players limit
    if tournament.registration.max_players:
        current_registrations = await data_layer.registrations.list_by_tournament(
            tournament_id, status=PlayerStatus.ACTIVE.value
        )
        if len(current_registrations) >= tournament.registration.max_players:
            max_players = tournament.registration.max_players
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tournament has reached maximum player count ({max_players})",
            )

    # Get next sequence ID
    sequence_id = await data_layer.registrations.get_next_sequence_id(tournament_id)

    # Create registration
    registration = TournamentRegistration(
        id=uuid4(),
        tournament_id=tournament_id,
        player_id=registration_data.player_id,
        sequence_id=sequence_id,
        status=PlayerStatus.ACTIVE,
        registration_time=datetime.now(timezone.utc),
        notes=registration_data.notes,
    )

    return await data_layer.registrations.create(registration)


@router.get("/{tournament_id}/registrations", response_model=list[TournamentRegistration])
async def list_registrations(
    tournament_id: UUID, data_layer: DataLayerDep, pagination: PaginationDep
) -> list[TournamentRegistration]:
    """
    List all registrations for a tournament.

    Returns registrations with status (active, dropped, etc.)
    sorted by sequence_id.
    """
    # Verify tournament exists
    try:
        await data_layer.tournaments.get_by_id(tournament_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament {tournament_id} not found"
        ) from None

    # List all registrations (no status filter to include dropped players)
    registrations = await data_layer.registrations.list_by_tournament(tournament_id)

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return registrations[start:end]


@router.delete("/{tournament_id}/registrations/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def drop_player(tournament_id: UUID, player_id: UUID, data_layer: DataLayerDep) -> None:
    """
    Drop a player from a tournament.

    Sets the player's status to DROPPED and records drop_time.
    Does not delete the registration (preserves history).
    """
    # Verify tournament exists
    try:
        await data_layer.tournaments.get_by_id(tournament_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament {tournament_id} not found"
        ) from None

    # Get registration
    registration = await data_layer.registrations.get_by_tournament_and_player(
        tournament_id, player_id
    )
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} is not registered for tournament {tournament_id}",
        )

    # Update registration status to DROPPED
    registration.status = PlayerStatus.DROPPED
    registration.drop_time = datetime.now(timezone.utc)

    await data_layer.registrations.update(registration)
    return
