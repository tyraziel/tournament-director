"""Database connection and session management.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.data.database.models import Base


class DatabaseConnection:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str) -> None:
        """Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL
                - SQLite: "sqlite+aiosqlite:///./tournament.db"
                - PostgreSQL: "postgresql+asyncpg://user:pass@localhost/dbname"
                - MySQL: "mysql+aiomysql://user:pass@localhost/dbname"
                - MariaDB: "mariadb+aiomysql://user:pass@localhost/dbname"
        """
        self.database_url = database_url
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before using
        )

        self.async_session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables. USE WITH CAUTION!"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        """Close database connection and dispose of engine."""
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create a new database session.

        Usage:
            async with db.session() as session:
                result = await session.execute(query)
                await session.commit()
        """
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
