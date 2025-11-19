"""Custom database types for cross-database compatibility.

Provides database-agnostic UUID and JSON types that work across:
- SQLite (uses TEXT for UUID, TEXT for JSON)
- PostgreSQL (uses native UUID and JSONB)
- MySQL (uses CHAR(36) for UUID, JSON for JSON)
- MariaDB (uses CHAR(36) for UUID, JSON for JSON)

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import json
from typing import Any
from uuid import UUID as PyUUID  # noqa: N811  # SQLAlchemy type alias

from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID  # noqa: N811


class UUID(TypeDecorator):
    """Database-agnostic UUID type.

    Stores UUIDs efficiently based on database backend:
    - PostgreSQL: Native UUID type
    - SQLite: CHAR(36) string (hyphenated format)
    - MySQL/MariaDB: CHAR(36) string (hyphenated format)

    Automatically converts between Python uuid.UUID objects and database storage.

    Example:
        class Player(Base):
            id: Mapped[PyUUID] = mapped_column(UUID(), primary_key=True)
    """

    impl = String(36)  # Default: CHAR(36) for MySQL/MariaDB/SQLite
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        """Select appropriate type based on database dialect."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQLUUID(as_uuid=True))
        # MySQL, MariaDB, SQLite: use CHAR(36)
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value: PyUUID | None, dialect: Any) -> str | None:
        """Convert Python UUID to database format."""
        if value is None:
            return None

        if not isinstance(value, PyUUID):
            raise TypeError(f"Expected UUID, got {type(value)}")

        # PostgreSQL handles UUID natively
        if dialect.name == "postgresql":
            return value  # type: ignore[return-value]

        # Other databases: convert to hyphenated string
        return str(value)

    def process_result_value(self, value: Any | None, dialect: Any) -> PyUUID | None:
        """Convert database format to Python UUID."""
        if value is None:
            return None

        # PostgreSQL returns UUID directly (if using native UUID type)
        if isinstance(value, PyUUID):
            return value

        # Other databases: parse string to UUID
        if isinstance(value, str):
            return PyUUID(value)

        raise TypeError(f"Unexpected UUID value type: {type(value)}")


class JSON(TypeDecorator):
    """Database-agnostic JSON type.

    Stores JSON data efficiently based on database backend:
    - PostgreSQL: JSONB (binary JSON, indexed)
    - MySQL 5.7+: Native JSON type
    - MariaDB 10.2+: Native JSON type (alias for LONGTEXT with validation)
    - SQLite: TEXT (serialized JSON string)

    Automatically serializes/deserializes Python dicts to/from database storage.

    Example:
        class Tournament(Base):
            config: Mapped[Dict[str, Any]] = mapped_column(JSON(), nullable=False)
    """

    impl = Text  # Default: TEXT for SQLite
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        """Select appropriate type based on database dialect."""
        if dialect.name == "postgresql":
            # PostgreSQL: Use JSONB for better performance and indexing
            return dialect.type_descriptor(JSONB())
        if dialect.name in ("mysql", "mariadb"):
            # MySQL/MariaDB 5.7+: Use native JSON type
            # Falls back to TEXT for older versions
            try:
                from sqlalchemy.dialects.mysql import JSON as MySQLJSON  # noqa: N811
                return dialect.type_descriptor(MySQLJSON())
            except ImportError:
                return dialect.type_descriptor(Text())
        else:
            # SQLite: Use TEXT
            return dialect.type_descriptor(Text())

    def process_bind_param(
        self,
        value: dict[str, Any] | None,
        dialect: Any
    ) -> Any | None:
        """Convert Python dict to database format."""
        if value is None:
            return None

        # PostgreSQL and MySQL handle dicts natively when using native JSON types
        if dialect.name in ("postgresql", "mysql", "mariadb"):
            return value

        # SQLite: Serialize to JSON string
        return json.dumps(value)

    def process_result_value(
        self,
        value: Any | None,
        dialect: Any
    ) -> dict[str, Any] | None:
        """Convert database format to Python dict."""
        if value is None:
            return None

        # PostgreSQL and MySQL return dicts directly (when using native types)
        if isinstance(value, dict):
            return value

        # SQLite: Deserialize JSON string
        if isinstance(value, str):
            return json.loads(value)  # type: ignore[no-any-return]

        raise TypeError(f"Unexpected JSON value type: {type(value)}")
