# Alembic Migrations Guide

**AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0**

## Overview

Alembic provides database schema version control for Tournament Director, supporting migrations across SQLite, PostgreSQL, MySQL, and MariaDB.

---

## Quick Start

### View Current Migration Version

```bash
alembic current
```

**Output:**
```
aa7161e6fd68 (head)
```

### Apply All Migrations (Upgrade to Latest)

```bash
alembic upgrade head
```

### Rollback One Migration

```bash
alembic downgrade -1
```

### Rollback to Specific Version

```bash
alembic downgrade <revision_id>
```

### Rollback All Migrations

```bash
alembic downgrade base
```

---

## Configuration

### Database URL Selection

Alembic reads the database URL from two sources (in priority order):

1. **Environment Variable** (`DATABASE_URL`)
2. **alembic.ini** (fallback default: SQLite)

**Example - Override with Environment Variable:**

```bash
# SQLite (file-based)
DATABASE_URL="sqlite+aiosqlite:///tournament.db" alembic upgrade head

# PostgreSQL
DATABASE_URL="postgresql+asyncpg://postgres@/tournament_director?host=/tmp/pg_socket" alembic upgrade head

# MySQL
DATABASE_URL="mysql+aiomysql://user:pass@localhost/tournament_director" alembic upgrade head

# MariaDB
DATABASE_URL="mariadb+aiomysql://user:pass@localhost/tournament_director" alembic upgrade head
```

### Default Configuration (alembic.ini)

```ini
sqlalchemy.url = sqlite+aiosqlite:///tournament.db
```

To change the default, edit `alembic.ini` line 93.

---

## Creating Migrations

### Auto-Generate Migration from Model Changes

Alembic can automatically detect changes in `src/data/database/models.py` and generate migration scripts:

```bash
alembic revision --autogenerate -m "Add player rating column"
```

**What gets detected:**
- New tables
- New columns
- Column type changes
- Foreign key changes
- Index changes
- Constraint changes

**What does NOT get detected automatically:**
- Renames (tables or columns) - requires manual edit
- Data migrations - requires manual script

### Manual Migration (for complex changes)

```bash
alembic revision -m "Migrate player data to new schema"
```

Edit the generated file in `alembic/versions/` to add custom logic.

---

## Migration Examples

### Example 1: Add Column

**Step 1: Update Model**

```python
# src/data/database/models.py
class PlayerModel(Base):
    # ...existing fields...
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

**Step 2: Generate Migration**

```bash
alembic revision --autogenerate -m "Add player rating column"
```

**Generated Migration:**

```python
def upgrade() -> None:
    op.add_column('players', sa.Column('rating', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('players', 'rating')
```

**Step 3: Apply Migration**

```bash
alembic upgrade head
```

### Example 2: Data Migration

Sometimes you need to migrate data, not just schema:

```bash
alembic revision -m "Set default player ratings"
```

**Edit the migration manually:**

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Step 1: Add column
    op.add_column('players', sa.Column('rating', sa.Integer(), nullable=True))

    # Step 2: Set default rating for existing players
    op.execute("UPDATE players SET rating = 1000 WHERE rating IS NULL")

    # Step 3: Make column non-nullable
    op.alter_column('players', 'rating', nullable=False)

def downgrade() -> None:
    op.drop_column('players', 'rating')
```

**Apply:**

```bash
alembic upgrade head
```

---

## Cross-Database Compatibility

### Custom Types

Our custom `UUID` and `JSON` types automatically adapt to each database:

| Database | UUID Type | JSON Type |
|----------|-----------|-----------|
| SQLite | CHAR(36) | TEXT (serialized) |
| PostgreSQL | UUID (native) | JSONB (native, indexed) |
| MySQL 5.7+ | CHAR(36) | JSON (native) |
| MariaDB 10.2+ | CHAR(36) | JSON (native) |

**In migrations, always use:**

```python
from src.data.database.types import UUID, JSON

def upgrade() -> None:
    op.create_table('new_table',
        sa.Column('id', UUID(length=36), nullable=False),
        sa.Column('data', JSON(), nullable=False),
    )
```

### Database-Specific Features

When you need database-specific migrations, use conditionals:

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    conn = op.get_bind()

    if conn.dialect.name == "postgresql":
        # PostgreSQL-specific: Add GIN index for JSONB
        op.execute("CREATE INDEX idx_config_gin ON tournaments USING GIN (registration)")
    elif conn.dialect.name in ("mysql", "mariadb"):
        # MySQL/MariaDB-specific: Add full-text index
        op.execute("CREATE FULLTEXT INDEX idx_description ON tournaments (description)")
    else:
        # SQLite: No special indexing
        pass
```

---

## Migration Workflow

### Development Workflow

1. **Pull latest code**
   ```bash
   git pull origin main
   ```

2. **Apply migrations to local database**
   ```bash
   alembic upgrade head
   ```

3. **Make model changes**
   Edit `src/data/database/models.py`

4. **Generate migration**
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```

5. **Review generated migration**
   Check `alembic/versions/<revision>_description.py`

6. **Test migration**
   ```bash
   # Test upgrade
   alembic upgrade head

   # Test downgrade
   alembic downgrade -1

   # Re-upgrade
   alembic upgrade head
   ```

7. **Commit migration**
   ```bash
   git add alembic/versions/<revision>_*.py
   git commit -m "Add migration: description"
   ```

### Production Deployment

1. **Backup database** (CRITICAL!)
   ```bash
   # PostgreSQL
   pg_dump tournament_director > backup_$(date +%Y%m%d_%H%M%S).sql

   # MySQL/MariaDB
   mysqldump tournament_director > backup_$(date +%Y%m%d_%H%M%S).sql

   # SQLite
   cp tournament.db tournament_backup_$(date +%Y%m%d_%H%M%S).db
   ```

2. **Pull latest code**
   ```bash
   git pull origin main
   ```

3. **Check migration status**
   ```bash
   alembic current
   alembic history
   ```

4. **Apply migrations**
   ```bash
   alembic upgrade head
   ```

5. **Verify application**
   Test application with new schema

6. **Rollback if needed**
   ```bash
   alembic downgrade <previous_revision>
   # Restore from backup if necessary
   ```

---

## Troubleshooting

### Error: "Can't locate revision identified by <revision>"

**Cause:** Migration file missing or alembic version table out of sync

**Solution:**
```bash
# Check migration files exist
ls alembic/versions/

# Reset version table (CAUTION: only if you know current state)
alembic stamp head
```

### Error: "Target database is not up to date"

**Cause:** Someone else added migrations you don't have

**Solution:**
```bash
git pull origin main
alembic upgrade head
```

### Error: Migration fails mid-way

**Cause:** Invalid SQL or data constraint violation

**Solution:**
```bash
# Check which migration is partially applied
alembic current

# Manually fix the issue (edit migration or fix data)

# Mark migration as complete if fixed manually
alembic stamp <revision>

# Or rollback if can't fix
alembic downgrade -1
```

### SQLite "no such column" after migration

**Cause:** SQLite doesn't support all ALTER TABLE operations

**Solution:** Use batch operations in migrations:

```python
def upgrade() -> None:
    with op.batch_alter_table('players') as batch_op:
        batch_op.add_column(sa.Column('rating', sa.Integer()))
```

---

## Testing Migrations

### Test Migration on All Databases

**Script: test_migrations.sh**

```bash
#!/bin/bash

# Test SQLite
echo "Testing SQLite..."
DATABASE_URL="sqlite+aiosqlite:///test.db" alembic upgrade head
DATABASE_URL="sqlite+aiosqlite:///test.db" alembic downgrade base
rm test.db

# Test PostgreSQL
echo "Testing PostgreSQL..."
DATABASE_URL="postgresql+asyncpg://postgres@/test_migrations?host=/tmp/pg_socket" alembic upgrade head
DATABASE_URL="postgresql+asyncpg://postgres@/test_migrations?host=/tmp/pg_socket" alembic downgrade base

# Test MySQL
echo "Testing MySQL..."
DATABASE_URL="mysql+aiomysql://test:test@localhost/test_migrations" alembic upgrade head
DATABASE_URL="mysql+aiomysql://test:test@localhost/test_migrations" alembic downgrade base

echo "All database migrations tested successfully!"
```

---

## Current Schema (Revision aa7161e6fd68)

### Tables Created

1. **formats** - Game formats (MTG, Pokemon, etc.)
2. **players** - Player registration and profiles
3. **venues** - Tournament venues
4. **tournaments** - Tournament metadata
5. **components** - Tournament components (Swiss, Single Elimination, etc.)
6. **tournament_registrations** - Player registrations per tournament
7. **rounds** - Round tracking per component
8. **matches** - Match results and pairings

### Foreign Keys

- tournaments → formats
- tournaments → venues
- tournaments → players (created_by)
- components → tournaments
- tournament_registrations → tournaments
- tournament_registrations → players
- rounds → tournaments
- rounds → components
- matches → tournaments
- matches → components
- matches → rounds
- matches → players (player1, player2)

---

## Best Practices

1. **Always review auto-generated migrations** - Alembic may not detect renames correctly
2. **Test migrations before deploying** - Run upgrade/downgrade cycle locally
3. **Backup before production migrations** - Always have rollback plan
4. **Use descriptive migration messages** - Makes history easier to navigate
5. **Never edit applied migrations** - Create new migration to fix issues
6. **Keep migrations small** - Easier to test and rollback
7. **Document complex migrations** - Add comments explaining business logic

---

## Related Documentation

- **MYSQL_MARIADB_COMPATIBILITY.md** - MySQL/MariaDB compatibility verification
- **src/data/database/types.py** - Custom UUID and JSON type implementations
- **src/data/database/models.py** - SQLAlchemy model definitions
- **alembic/env.py** - Async migration environment configuration

---

**Last Updated:** 2025-01-19
**Current Migration:** aa7161e6fd68 (Initial schema)
**Supported Databases:** SQLite, PostgreSQL, MySQL 5.7+, MariaDB 10.2+
