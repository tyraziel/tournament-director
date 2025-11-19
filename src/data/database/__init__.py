"""Database backend implementation for Tournament Director.

Supports SQLite, PostgreSQL, MySQL, and MariaDB via SQLAlchemy.

Usage:
    from src.data.database import DatabaseDataLayer

    # SQLite (zero config)
    data_layer = DatabaseDataLayer("sqlite+aiosqlite:///./tournament.db")

    # PostgreSQL
    data_layer = DatabaseDataLayer("postgresql+asyncpg://user:pass@localhost/tournament_director")

    # MySQL
    data_layer = DatabaseDataLayer("mysql+aiomysql://user:pass@localhost/tournament_director")

    # MariaDB
    data_layer = DatabaseDataLayer("mariadb+aiomysql://user:pass@localhost/tournament_director")

    # Initialize
    await data_layer.initialize()

    # Use
    players = await data_layer.players.list_all()
    await data_layer.commit()

    # Clean up
    await data_layer.close()

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from src.data.database.data_layer import DatabaseDataLayer

__all__ = ["DatabaseDataLayer"]
