"""Data layer exceptions.

AIA PAI Hin R Claude Code v1.0
"""

from typing import Any
from uuid import UUID

# Type alias for dictionaries with string keys
Details = dict[str, Any]


class DataLayerError(Exception):
    """Base exception for all data layer errors."""

    def __init__(self, message: str, details: Details | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(DataLayerError):
    """Raised when a requested entity is not found."""

    def __init__(self, entity_type: str, entity_id: UUID, details: Details | None = None):
        message = f"{entity_type} with id {entity_id} not found"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateError(DataLayerError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(self, entity_type: str, field: str, value: Any, details: Details | None = None):
        message = f"{entity_type} with {field}='{value}' already exists"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.field = field
        self.value = value


class ValidationError(DataLayerError):
    """Raised when data validation fails."""

    def __init__(
        self,
        entity_type: str,
        field: str,
        value: Any,
        reason: str,
        details: Details | None = None,
    ):
        message = f"Validation failed for {entity_type}.{field}='{value}': {reason}"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.field = field
        self.value = value
        self.reason = reason


class IntegrityError(DataLayerError):
    """Raised when referential integrity is violated."""

    def __init__(
        self, message: str, entity_type: str, constraint: str, details: Details | None = None
    ):
        super().__init__(message, details)
        self.entity_type = entity_type
        self.constraint = constraint
