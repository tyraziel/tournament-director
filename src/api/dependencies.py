"""
Dependency injection for FastAPI endpoints.

Provides shared resources like data layer instances for API endpoints.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from typing import Annotated

from fastapi import Depends

from src.api.config import config
from src.data.interface import DataLayer
from src.data.local import LocalDataLayer
from src.data.mock import MockDataLayer

# Singleton data layer instance
_data_layer: DataLayer | None = None


def get_data_layer() -> DataLayer:
    """
    Get data layer instance (singleton).

    Returns the configured data layer backend (mock, local, or database).
    Creates the instance on first call and reuses it for subsequent calls.
    """
    global _data_layer

    if _data_layer is None:
        if config.data_backend == "mock":
            _data_layer = MockDataLayer()
        elif config.data_backend == "local":
            _data_layer = LocalDataLayer(config.local_data_path)
        else:
            # TODO: Add database backend when implemented
            raise NotImplementedError(f"Backend '{config.data_backend}' not yet implemented")

    return _data_layer


# Type alias for dependency injection
DataLayerDep = Annotated[DataLayer, Depends(get_data_layer)]


# Pagination dependencies
def get_pagination_params(
    limit: int = config.default_page_size,
    offset: int = 0,
) -> dict[str, int]:
    """
    Get pagination parameters with validation.

    Args:
        limit: Maximum number of items to return (default: 20, max: 100)
        offset: Number of items to skip (default: 0)

    Returns:
        Dictionary with validated limit and offset
    """
    # Validate and cap limit
    limit = min(limit, config.max_page_size)
    limit = max(limit, 1)

    # Validate offset
    offset = max(offset, 0)

    return {"limit": limit, "offset": offset}


PaginationDep = Annotated[dict[str, int], Depends(get_pagination_params)]
