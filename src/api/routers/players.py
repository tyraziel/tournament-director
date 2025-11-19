"""
Player management endpoints.

Provides CRUD operations for player entities.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DataLayerDep, PaginationDep
from src.data.exceptions import DuplicateError, NotFoundError
from src.models.player import Player, PlayerCreate, PlayerUpdate

router = APIRouter()


@router.get(
    "/",
    summary="List all players",
    description="Retrieve a paginated list of all players",
    response_model=list[Player],
    status_code=status.HTTP_200_OK,
)
async def list_players(
    data_layer: DataLayerDep,
    pagination: PaginationDep,
) -> list[Player]:
    """
    List all players with pagination.

    Args:
        limit: Maximum number of players to return
        offset: Number of players to skip

    Returns:
        List of Player objects
    """
    players = await data_layer.players.list_all()

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return players[start:end]


@router.post(
    "/",
    summary="Create a new player",
    description="Create a new player in the system",
    response_model=Player,
    status_code=status.HTTP_201_CREATED,
)
async def create_player(
    player_data: PlayerCreate,
    data_layer: DataLayerDep,
) -> Player:
    """
    Create a new player.

    Args:
        player_data: Player creation data (name, discord_id, email)

    Returns:
        Created Player object with generated ID

    Raises:
        409: Player with same discord_id or email already exists
    """
    from uuid import uuid4

    # Convert PlayerCreate to Player (generates UUID)
    player = Player(id=uuid4(), **player_data.model_dump())

    try:
        return await data_layer.players.create(player)
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.get(
    "/{player_id}",
    summary="Get player by ID",
    description="Retrieve a specific player by their UUID",
    response_model=Player,
    status_code=status.HTTP_200_OK,
)
async def get_player(
    player_id: UUID,
    data_layer: DataLayerDep,
) -> Player:
    """
    Get a player by ID.

    Args:
        player_id: Player UUID

    Returns:
        Player object

    Raises:
        404: Player not found
    """
    try:
        return await data_layer.players.get_by_id(player_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        ) from None


@router.put(
    "/{player_id}",
    summary="Update player",
    description="Update an existing player's information",
    response_model=Player,
    status_code=status.HTTP_200_OK,
)
async def update_player(
    player_id: UUID,
    player_data: PlayerUpdate,
    data_layer: DataLayerDep,
) -> Player:
    """
    Update a player.

    Args:
        player_id: Player UUID
        player_data: Player update data

    Returns:
        Updated Player object

    Raises:
        404: Player not found
        409: Update would create duplicate discord_id or email
    """
    try:
        # Get existing player
        existing_player = await data_layer.players.get_by_id(player_id)

        # Apply updates (only non-None fields)
        update_dict = player_data.model_dump(exclude_unset=True)
        updated_player = existing_player.model_copy(update=update_dict)

        # Save to data layer
        return await data_layer.players.update(updated_player)

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        ) from None
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.delete(
    "/{player_id}",
    summary="Delete player",
    description="Delete a player from the system",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_player(
    player_id: UUID,
    data_layer: DataLayerDep,
) -> None:
    """
    Delete a player.

    Args:
        player_id: Player UUID

    Raises:
        404: Player not found
    """
    try:
        await data_layer.players.delete(player_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        ) from None


@router.get(
    "/search/by-name",
    summary="Search players by name",
    description="Search for players by name (case-insensitive partial match)",
    response_model=list[Player],
    status_code=status.HTTP_200_OK,
)
async def search_players_by_name(
    name: str,
    data_layer: DataLayerDep,
    pagination: PaginationDep,
) -> list[Player]:
    """
    Search for players by name.

    Args:
        name: Name to search for (partial match, case-insensitive)
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of matching Player objects
    """
    all_players = await data_layer.players.list_all()

    # Filter by name (case-insensitive partial match)
    name_lower = name.lower()
    matching_players = [player for player in all_players if name_lower in player.name.lower()]

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return matching_players[start:end]


@router.get(
    "/discord/{discord_id}",
    summary="Get player by Discord ID",
    description="Retrieve a player by their Discord ID",
    response_model=Player,
    status_code=status.HTTP_200_OK,
)
async def get_player_by_discord_id(
    discord_id: str,
    data_layer: DataLayerDep,
) -> Player:
    """
    Get a player by Discord ID.

    Args:
        discord_id: Discord user ID

    Returns:
        Player object

    Raises:
        404: Player not found
    """
    player = await data_layer.players.get_by_discord_id(discord_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with Discord ID {discord_id} not found",
        )
    return player
