"""
Format management endpoints.

Provides CRUD operations for format entities.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DataLayerDep, PaginationDep
from src.data.exceptions import DuplicateError, NotFoundError
from src.models.base import GameSystem
from src.models.format import Format, FormatCreate, FormatUpdate

router = APIRouter()


@router.get(
    "/",
    summary="List all formats",
    description="Retrieve a paginated list of all formats",
    response_model=list[Format],
    status_code=status.HTTP_200_OK,
)
async def list_formats(
    data_layer: DataLayerDep,
    pagination: PaginationDep,
    game_system: GameSystem | None = None,
) -> list[Format]:
    """
    List all formats with optional filtering by game system.

    Args:
        limit: Maximum number of formats to return
        offset: Number of formats to skip
        game_system: Optional filter by game system

    Returns:
        List of Format objects
    """
    if game_system:
        formats = await data_layer.formats.list_by_game_system(game_system.value)
    else:
        formats = await data_layer.formats.list_all()

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return formats[start:end]


@router.post(
    "/",
    summary="Create a new format",
    description="Create a new format in the system",
    response_model=Format,
    status_code=status.HTTP_201_CREATED,
)
async def create_format(
    format_data: FormatCreate,
    data_layer: DataLayerDep,
) -> Format:
    """
    Create a new format.

    Args:
        format_data: Format creation data

    Returns:
        Created Format object with generated ID

    Raises:
        409: Format with same game_system and name already exists
    """
    # Convert FormatCreate to Format (generates UUID)
    format_obj = Format(id=uuid4(), **format_data.model_dump())

    try:
        return await data_layer.formats.create(format_obj)
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.get(
    "/{format_id}",
    summary="Get format by ID",
    description="Retrieve a specific format by its UUID",
    response_model=Format,
    status_code=status.HTTP_200_OK,
)
async def get_format(
    format_id: UUID,
    data_layer: DataLayerDep,
) -> Format:
    """
    Get a format by ID.

    Args:
        format_id: Format UUID

    Returns:
        Format object

    Raises:
        404: Format not found
    """
    try:
        return await data_layer.formats.get_by_id(format_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format {format_id} not found",
        ) from None


@router.put(
    "/{format_id}",
    summary="Update format",
    description="Update an existing format's information",
    response_model=Format,
    status_code=status.HTTP_200_OK,
)
async def update_format(
    format_id: UUID,
    format_data: FormatUpdate,
    data_layer: DataLayerDep,
) -> Format:
    """
    Update a format.

    Args:
        format_id: Format UUID
        format_data: Format update data

    Returns:
        Updated Format object

    Raises:
        404: Format not found
        409: Update would create duplicate game_system + name
    """
    try:
        # Get existing format
        existing_format = await data_layer.formats.get_by_id(format_id)

        # Apply updates (only non-None fields)
        update_dict = format_data.model_dump(exclude_unset=True)
        updated_format = existing_format.model_copy(update=update_dict)

        # Save to data layer
        return await data_layer.formats.update(updated_format)

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format {format_id} not found",
        ) from None
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.delete(
    "/{format_id}",
    summary="Delete format",
    description="Delete a format from the system",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_format(
    format_id: UUID,
    data_layer: DataLayerDep,
) -> None:
    """
    Delete a format.

    Args:
        format_id: Format UUID

    Raises:
        404: Format not found
    """
    try:
        await data_layer.formats.delete(format_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format {format_id} not found",
        ) from None


@router.get(
    "/game/{game_system}",
    summary="List formats by game system",
    description="Retrieve all formats for a specific game system",
    response_model=list[Format],
    status_code=status.HTTP_200_OK,
)
async def list_formats_by_game(
    game_system: GameSystem,
    data_layer: DataLayerDep,
    pagination: PaginationDep,
) -> list[Format]:
    """
    List all formats for a specific game system.

    Args:
        game_system: Game system to filter by
        limit: Maximum number of formats to return
        offset: Number of formats to skip

    Returns:
        List of Format objects for the specified game system
    """
    formats = await data_layer.formats.list_by_game_system(game_system.value)

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return formats[start:end]
