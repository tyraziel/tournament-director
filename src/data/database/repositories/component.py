"""Database repository for Component entities.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.exceptions import DuplicateError, NotFoundError
from src.data.interface import ComponentRepository
from src.data.database.models import ComponentModel
from src.models.match import Component
from src.models.base import ComponentType, ComponentStatus


class DatabaseComponentRepository(ComponentRepository):
    """Database implementation of ComponentRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    def _to_pydantic(self, db_component: ComponentModel) -> Component:
        """Convert database model to Pydantic model."""
        return Component(
            id=db_component.id,
            tournament_id=db_component.tournament_id,
            type=ComponentType(db_component.type),
            name=db_component.name,
            sequence_order=db_component.sequence_order,
            status=ComponentStatus(db_component.status),
            config=db_component.config,
            created_at=db_component.created_at,
        )

    async def create(self, component: Component) -> Component:
        """Create a new component."""
        # Check for duplicate ID
        existing = await self.session.get(ComponentModel, component.id)
        if existing:
            raise DuplicateError(f"Component with ID {component.id} already exists")

        db_component = ComponentModel(
            id=component.id,
            tournament_id=component.tournament_id,
            type=component.type.value,
            name=component.name,
            sequence_order=component.sequence_order,
            status=component.status.value,
            config=component.config,
            created_at=component.created_at,
        )

        self.session.add(db_component)
        await self.session.flush()

        return component

    async def get_by_id(self, component_id: UUID) -> Component:
        """Get component by ID. Raises NotFoundError if not found."""
        db_component = await self.session.get(ComponentModel, component_id)
        if not db_component:
            raise NotFoundError(f"Component with ID {component_id} not found")

        return self._to_pydantic(db_component)

    async def list_by_tournament(self, tournament_id: UUID) -> List[Component]:
        """List components for a tournament, ordered by sequence_order."""
        stmt = select(ComponentModel).where(
            ComponentModel.tournament_id == tournament_id
        ).order_by(ComponentModel.sequence_order)

        result = await self.session.execute(stmt)
        db_components = result.scalars().all()

        return [self._to_pydantic(db_component) for db_component in db_components]

    async def get_by_tournament_and_sequence(
        self, tournament_id: UUID, sequence_order: int
    ) -> Optional[Component]:
        """Get component by tournament and sequence order. Returns None if not found."""
        stmt = select(ComponentModel).where(
            ComponentModel.tournament_id == tournament_id,
            ComponentModel.sequence_order == sequence_order
        )
        result = await self.session.execute(stmt)
        db_component = result.scalar_one_or_none()

        if not db_component:
            return None

        return self._to_pydantic(db_component)

    async def update(self, component: Component) -> Component:
        """Update an existing component."""
        db_component = await self.session.get(ComponentModel, component.id)
        if not db_component:
            raise NotFoundError(f"Component with ID {component.id} not found")

        db_component.type = component.type.value
        db_component.name = component.name
        db_component.sequence_order = component.sequence_order
        db_component.status = component.status.value
        db_component.config = component.config
        # created_at is immutable

        await self.session.flush()

        return component

    async def delete(self, component_id: UUID) -> None:
        """Delete a component. Raises NotFoundError if not found."""
        db_component = await self.session.get(ComponentModel, component_id)
        if not db_component:
            raise NotFoundError(f"Component with ID {component_id} not found")

        await self.session.delete(db_component)
        await self.session.flush()
