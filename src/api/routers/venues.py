"""
Venue management endpoints.

Provides CRUD operations for venue entities.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DataLayerDep, PaginationDep
from src.data.exceptions import DuplicateError, NotFoundError
from src.models.venue import Venue, VenueCreate, VenueUpdate

router = APIRouter()


@router.get(
    "/",
    summary="List all venues",
    description="Retrieve a paginated list of all venues",
    response_model=list[Venue],
    status_code=status.HTTP_200_OK,
)
async def list_venues(
    data_layer: DataLayerDep,
    pagination: PaginationDep,
) -> list[Venue]:
    """
    List all venues with pagination.

    Args:
        limit: Maximum number of venues to return
        offset: Number of venues to skip

    Returns:
        List of Venue objects
    """
    venues = await data_layer.venues.list_all()

    # Apply pagination
    start = pagination["offset"]
    end = start + pagination["limit"]
    return venues[start:end]


@router.post(
    "/",
    summary="Create a new venue",
    description="Create a new venue in the system",
    response_model=Venue,
    status_code=status.HTTP_201_CREATED,
)
async def create_venue(
    venue_data: VenueCreate,
    data_layer: DataLayerDep,
) -> Venue:
    """
    Create a new venue.

    Args:
        venue_data: Venue creation data (name, address, description)

    Returns:
        Created Venue object with generated ID

    Raises:
        409: Venue with same name already exists
    """
    from uuid import uuid4

    # Convert VenueCreate to Venue (generates UUID)
    venue = Venue(id=uuid4(), **venue_data.model_dump())

    try:
        return await data_layer.venues.create(venue)
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.get(
    "/{venue_id}",
    summary="Get venue by ID",
    description="Retrieve a specific venue by its UUID",
    response_model=Venue,
    status_code=status.HTTP_200_OK,
)
async def get_venue(
    venue_id: UUID,
    data_layer: DataLayerDep,
) -> Venue:
    """
    Get a venue by ID.

    Args:
        venue_id: Venue UUID

    Returns:
        Venue object

    Raises:
        404: Venue not found
    """
    try:
        return await data_layer.venues.get_by_id(venue_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue {venue_id} not found",
        ) from None


@router.put(
    "/{venue_id}",
    summary="Update venue",
    description="Update an existing venue's information",
    response_model=Venue,
    status_code=status.HTTP_200_OK,
)
async def update_venue(
    venue_id: UUID,
    venue_data: VenueUpdate,
    data_layer: DataLayerDep,
) -> Venue:
    """
    Update a venue.

    Args:
        venue_id: Venue UUID
        venue_data: Venue update data

    Returns:
        Updated Venue object

    Raises:
        404: Venue not found
        409: Update would create duplicate name
    """
    try:
        # Get existing venue
        existing_venue = await data_layer.venues.get_by_id(venue_id)

        # Apply updates (only non-None fields)
        update_dict = venue_data.model_dump(exclude_unset=True)
        updated_venue = existing_venue.model_copy(update=update_dict)

        # Save to data layer
        return await data_layer.venues.update(updated_venue)

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue {venue_id} not found",
        ) from None
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.delete(
    "/{venue_id}",
    summary="Delete venue",
    description="Delete a venue from the system",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_venue(
    venue_id: UUID,
    data_layer: DataLayerDep,
) -> None:
    """
    Delete a venue.

    Args:
        venue_id: Venue UUID

    Raises:
        404: Venue not found
    """
    try:
        await data_layer.venues.delete(venue_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue {venue_id} not found",
        ) from None
