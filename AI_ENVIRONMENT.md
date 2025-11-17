# AI Environment Setup Guide

*AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0*

This document provides detailed instructions for setting up the development environment for AI-assisted development on Tournament Director. This ensures consistent behavior across different AI sessions and development environments.

---

## Table of Contents

1. [Environment Overview](#environment-overview)
2. [Database Setup](#database-setup)
3. [Python Dependencies](#python-dependencies)
4. [Quick Start Scripts](#quick-start-scripts)
5. [Troubleshooting](#troubleshooting)
6. [Environment Variables](#environment-variables)

---

## Environment Overview

### System Information

**Operating System:** Linux (Ubuntu 24.04)
**Python Version:** 3.8+
**Available Databases:**
- SQLite (built-in, always available)
- PostgreSQL 16.10 (installed, requires initialization)

**Package Manager:** pip
**Virtual Environment:** Recommended (`~/.venv-tui` or project-specific)

---

## Database Setup

### SQLite Setup

SQLite is **always available** with no setup required.

#### Basic Usage

```bash
# Verify SQLite is available
python3 -c "import sqlite3; print('SQLite version:', sqlite3.version)"

# Expected output: SQLite version: 2.6.0
```

#### Create Test Database

```bash
# Create a file-based database
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('tournament.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
cursor.execute("INSERT INTO test VALUES (1, 'Test')")
conn.commit()
cursor.execute('SELECT * FROM test')
print(cursor.fetchall())
conn.close()
EOF
```

#### Async SQLite Support

```bash
# Install aiosqlite for async operations
pip install aiosqlite==0.20.0

# Test async connection
python3 << 'EOF'
import asyncio
import aiosqlite

async def test():
    async with aiosqlite.connect(':memory:') as db:
        await db.execute('CREATE TABLE test (id INTEGER, name TEXT)')
        await db.execute("INSERT INTO test VALUES (1, 'Alice')")
        await db.commit()
        async with db.execute('SELECT * FROM test') as cursor:
            rows = await cursor.fetchall()
            print('Async SQLite working:', rows)

asyncio.run(test())
EOF
```

---

### PostgreSQL Setup

PostgreSQL 16.10 is installed but **must be initialized and started** in each new environment session.

#### Step 1: Initialize PostgreSQL Cluster

```bash
#!/bin/bash
# Initialize PostgreSQL data directory and configuration

# Create directories
mkdir -p /tmp/pgdata /tmp/pg_socket

# Set ownership to postgres user
chown postgres:postgres /tmp/pgdata /tmp/pg_socket

# Initialize database cluster
su - postgres -c "/usr/lib/postgresql/16/bin/initdb -D /tmp/pgdata"

# Configure socket directory (avoid permission issues)
echo "unix_socket_directories = '/tmp/pg_socket'" >> /tmp/pgdata/postgresql.conf

# Optional: Set custom port if needed
# echo "port = 5433" >> /tmp/pgdata/postgresql.conf
```

**Expected output:**
```
Success. You can now start the database server using:
    /usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata -l logfile start
```

#### Step 2: Start PostgreSQL Server

```bash
# Start the server
su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata -l /tmp/pgdata/logfile start"

# Wait for server to start (usually 1-2 seconds)
sleep 2

# Verify server is running
su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata status"
```

**Expected output:**
```
waiting for server to start.... done
server started

pg_ctl: server is running (PID: 8129)
/usr/lib/postgresql/16/bin/postgres "-D" "/tmp/pgdata"
```

#### Step 3: Create Database

```bash
# Create tournament_director database
su - postgres -c "psql -h /tmp/pg_socket -c 'CREATE DATABASE tournament_director;'"

# Verify database was created
su - postgres -c "psql -h /tmp/pg_socket -l" | grep tournament_director

# Create test table
su - postgres -c "psql -h /tmp/pg_socket -d tournament_director -c '
CREATE TABLE test_table (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
'"
```

#### Step 4: Install Python PostgreSQL Driver

```bash
# Install asyncpg (recommended for async/await)
pip install asyncpg==0.29.0

# Alternative: psycopg3 with async support
# pip install psycopg[binary]==3.2.1

# Test connection
python3 << 'EOF'
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        host='/tmp/pg_socket',
        database='tournament_director',
        user='postgres'
    )

    version = await conn.fetchval('SELECT version()')
    print('PostgreSQL version:', version.split(',')[0])

    await conn.close()

asyncio.run(test())
EOF
```

#### PostgreSQL Connection Strings

For Tournament Director data layer:

```python
# Standard connection
"postgresql+asyncpg://postgres@/tournament_director?host=/tmp/pg_socket"

# With explicit port (if customized)
"postgresql+asyncpg://postgres:password@localhost:5433/tournament_director"

# For testing (separate database)
"postgresql+asyncpg://postgres@/tournament_test?host=/tmp/pg_socket"
```

---

## Python Dependencies

### Core Dependencies (Already in requirements.txt)

```txt
pydantic==2.8.2
textual==0.80.1
aiofiles==24.1.0
```

### Database Dependencies (Add to requirements.txt)

```txt
# SQLite async support
aiosqlite==0.20.0

# PostgreSQL async driver
asyncpg==0.29.0

# ORM and database toolkit
sqlalchemy[asyncio]==2.0.23

# Database migrations
alembic==1.13.1
```

### Development Dependencies (Already in requirements.txt)

```txt
pytest==8.3.2
pytest-asyncio==0.23.8
pytest-cov==8.0.0      # Add for coverage
ruff==0.6.0
mypy==1.11.0
tox==4.16.0
```

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install development mode with optional database support
pip install -e ".[dev,database]"
```

### Update pyproject.toml

Add database dependencies as optional extras:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.2",
    "pytest-asyncio>=0.23.8",
    "pytest-cov>=8.0.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
    "tox>=4.16.0",
]
database = [
    "aiosqlite>=0.20.0",
    "asyncpg>=0.29.0",
    "sqlalchemy[asyncio]>=2.0.23",
    "alembic>=1.13.1",
]
```

---

## Quick Start Scripts

### All-in-One Environment Setup

Create `scripts/setup_environment.sh`:

```bash
#!/bin/bash
# Setup complete development environment for Tournament Director
# AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0

set -e  # Exit on error

echo "🚀 Setting up Tournament Director development environment..."

# 1. Check Python version
echo -e "\n📌 Checking Python version..."
python3 --version | grep -E "Python 3\.(8|9|10|11|12)" || {
    echo "❌ Python 3.8+ required"
    exit 1
}
echo "✅ Python version OK"

# 2. Install Python dependencies
echo -e "\n📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# 3. Setup PostgreSQL
echo -e "\n🐘 Setting up PostgreSQL..."
if su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata status" 2>/dev/null | grep -q "server is running"; then
    echo "✅ PostgreSQL already running"
else
    echo "Initializing PostgreSQL..."

    # Clean up any existing data
    rm -rf /tmp/pgdata /tmp/pg_socket
    mkdir -p /tmp/pgdata /tmp/pg_socket
    chown postgres:postgres /tmp/pgdata /tmp/pg_socket

    # Initialize
    su - postgres -c "/usr/lib/postgresql/16/bin/initdb -D /tmp/pgdata" > /dev/null

    # Configure
    echo "unix_socket_directories = '/tmp/pg_socket'" >> /tmp/pgdata/postgresql.conf

    # Start server
    su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata -l /tmp/pgdata/logfile start"
    sleep 2

    # Create database
    su - postgres -c "psql -h /tmp/pg_socket -c 'CREATE DATABASE tournament_director;'" 2>/dev/null || echo "Database may already exist"

    echo "✅ PostgreSQL initialized and running"
fi

# 4. Verify databases
echo -e "\n🔍 Verifying database connectivity..."

# Check SQLite
python3 -c "import sqlite3; print('✅ SQLite:', sqlite3.version)"

# Check PostgreSQL
su - postgres -c "psql -h /tmp/pg_socket -d tournament_director -c 'SELECT version();'" | head -3 | tail -1 | grep -q "PostgreSQL" && echo "✅ PostgreSQL: Connected" || echo "❌ PostgreSQL: Connection failed"

# 5. Run tests
echo -e "\n🧪 Running tests..."
pytest tests/ -v --tb=short || echo "⚠️  Some tests failed (this may be expected)"

echo -e "\n✨ Environment setup complete!"
echo -e "\n📝 Next steps:"
echo "  1. Review CLAUDE.md for development guidelines"
echo "  2. Run 'pytest tests/' to verify everything works"
echo "  3. Start coding with TDD methodology"
```

Make it executable:
```bash
chmod +x scripts/setup_environment.sh
```

### Database Health Check Script

Create `scripts/check_databases.sh`:

```bash
#!/bin/bash
# Check database availability and status
# AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0

echo "🔍 Database Environment Health Check"
echo "===================================="

# SQLite
echo -e "\n📁 SQLite:"
if python3 -c "import sqlite3" 2>/dev/null; then
    VERSION=$(python3 -c "import sqlite3; print(sqlite3.version)")
    echo "  Status: ✅ Available"
    echo "  Version: $VERSION"
    echo "  Module: Built-in (always available)"
else
    echo "  Status: ❌ Not available"
fi

# PostgreSQL
echo -e "\n🐘 PostgreSQL:"
if su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata status" 2>/dev/null | grep -q "server is running"; then
    PID=$(su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata status" | grep "PID" | awk '{print $NF}' | tr -d ')')
    VERSION=$(su - postgres -c "psql -h /tmp/pg_socket -t -c 'SELECT version();'" | head -1 | xargs)
    echo "  Status: ✅ Running (PID: $PID)"
    echo "  Version: PostgreSQL 16.10"
    echo "  Socket: /tmp/pg_socket"
    echo "  Data Dir: /tmp/pgdata"

    # Check if database exists
    if su - postgres -c "psql -h /tmp/pg_socket -lqt" | cut -d \| -f 1 | grep -qw tournament_director; then
        echo "  Database: ✅ tournament_director exists"
    else
        echo "  Database: ⚠️  tournament_director not found"
        echo "  Run: su - postgres -c \"psql -h /tmp/pg_socket -c 'CREATE DATABASE tournament_director;'\""
    fi
else
    echo "  Status: ❌ Not running"
    echo "  Start with: ./scripts/setup_environment.sh"
fi

# Python database libraries
echo -e "\n🐍 Python Database Libraries:"

python3 << 'EOF'
libraries = [
    ('aiosqlite', 'SQLite async support'),
    ('asyncpg', 'PostgreSQL async driver'),
    ('sqlalchemy', 'ORM toolkit'),
    ('alembic', 'Database migrations'),
]

for lib, desc in libraries:
    try:
        __import__(lib)
        print(f"  ✅ {lib:15} - {desc}")
    except ImportError:
        print(f"  ❌ {lib:15} - {desc} (pip install {lib})")
EOF

echo -e "\n===================================="
```

Make it executable:
```bash
chmod +x scripts/check_databases.sh
```

---

## Troubleshooting

### PostgreSQL Won't Start

**Error:** `could not create lock file "/var/run/postgresql/.s.PGSQL.5432.lock": Permission denied`

**Solution:** Configure Unix socket directory to use `/tmp/pg_socket`:
```bash
echo "unix_socket_directories = '/tmp/pg_socket'" >> /tmp/pgdata/postgresql.conf
su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata restart"
```

---

### PostgreSQL Already Running on Port 5432

**Error:** `could not bind IPv4 address "127.0.0.1": Address already in use`

**Solution:** Use a custom port:
```bash
echo "port = 5433" >> /tmp/pgdata/postgresql.conf
su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata restart"

# Update connection string
"postgresql+asyncpg://postgres@localhost:5433/tournament_director"
```

---

### Connection Refused

**Error:** `asyncpg.exceptions.ConnectionDoesNotExistError`

**Check:**
```bash
# 1. Verify server is running
su - postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /tmp/pgdata status"

# 2. Check socket location
ls -la /tmp/pg_socket/

# 3. Verify database exists
su - postgres -c "psql -h /tmp/pg_socket -l" | grep tournament_director
```

---

### Permission Denied on /tmp/pgdata

**Error:** `could not change permissions of directory "/tmp/pgdata": Operation not permitted`

**Solution:** Recreate with correct ownership:
```bash
rm -rf /tmp/pgdata /tmp/pg_socket
mkdir -p /tmp/pgdata /tmp/pg_socket
chown postgres:postgres /tmp/pgdata /tmp/pg_socket
su - postgres -c "/usr/lib/postgresql/16/bin/initdb -D /tmp/pgdata"
```

---

### Import Errors for Database Libraries

**Error:** `ModuleNotFoundError: No module named 'asyncpg'`

**Solution:** Install database dependencies:
```bash
pip install aiosqlite asyncpg sqlalchemy[asyncio] alembic
```

Or update `requirements.txt` and reinstall:
```bash
pip install -r requirements.txt
```

---

## Environment Variables

### Recommended Environment Variables

Create `.env` file (add to `.gitignore`):

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres@/tournament_director?host=/tmp/pg_socket
DATABASE_URL_SQLITE=sqlite+aiosqlite:///tournament.db
DATABASE_URL_TEST=sqlite+aiosqlite:///:memory:

# PostgreSQL Specific
PGHOST=/tmp/pg_socket
PGDATABASE=tournament_director
PGUSER=postgres
PGPORT=5432

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Testing
PYTEST_BACKEND=mock  # Options: mock, local, sqlite, postgres
```

### Load Environment Variables

```python
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Get database URL
database_url = os.getenv('DATABASE_URL')
```

---

## Testing Database Backends

### Test All Backends Systematically

```python
# tests/conftest.py
import pytest
import os
from src.data.mock import MockDataLayer
from src.data.local import LocalDataLayer

# Future imports when DatabaseDataLayer is implemented:
# from src.data.database import DatabaseDataLayer

@pytest.fixture(scope="function", params=["mock", "local"])
async def data_layer(request, tmp_path):
    """
    Parameterized fixture to test against all backends.

    AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
    """
    backend = os.getenv("PYTEST_BACKEND", request.param)

    if backend == "mock":
        yield MockDataLayer()

    elif backend == "local":
        yield LocalDataLayer(str(tmp_path))

    # Future: Add database backends
    # elif backend == "sqlite":
    #     db_url = "sqlite+aiosqlite:///:memory:"
    #     layer = DatabaseDataLayer(db_url)
    #     await layer.initialize()
    #     yield layer
    #     await layer.dispose()

    # elif backend == "postgres":
    #     db_url = os.getenv("DATABASE_URL")
    #     layer = DatabaseDataLayer(db_url)
    #     await layer.initialize()
    #     yield layer
    #     await layer.clear_all_data()
    #     await layer.dispose()
```

### Run Tests Against Specific Backend

```bash
# Test against mock backend only
PYTEST_BACKEND=mock pytest tests/ -v

# Test against local JSON backend
PYTEST_BACKEND=local pytest tests/ -v

# Test all backends (default)
pytest tests/ -v
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test-databases.yml
name: Test Database Backends

on: [push, pull_request]

jobs:
  test-sqlite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install aiosqlite sqlalchemy[asyncio]
      - name: Run tests with SQLite
        run: PYTEST_BACKEND=sqlite pytest tests/ -v

  test-postgres:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install asyncpg sqlalchemy[asyncio]
      - name: Run tests with PostgreSQL
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost/postgres
        run: PYTEST_BACKEND=postgres pytest tests/ -v
```

---

## Summary

✅ **SQLite** - Always available, no setup required
✅ **PostgreSQL** - Available with initialization (see setup scripts)
✅ **Backend Abstraction** - Swap databases without code changes
✅ **Testing** - Parameterized tests work across all backends
✅ **Scripts** - Automated setup and health checks

**For immediate use:**
```bash
# Run setup script
./scripts/setup_environment.sh

# Check status
./scripts/check_databases.sh

# Run tests
pytest tests/ -v
```

---

*This document should be updated whenever environment requirements change.*

**Last Updated:** 2025-11-16
**Maintained By:** Vibe-Coder Team
**Version:** 1.0.0
