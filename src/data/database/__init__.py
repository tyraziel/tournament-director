"""Database backend implementation for Tournament Director.

Supports SQLite, PostgreSQL, MySQL, and MariaDB via SQLAlchemy.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from src.data.database.data_layer import DatabaseDataLayer

__all__ = ["DatabaseDataLayer"]
