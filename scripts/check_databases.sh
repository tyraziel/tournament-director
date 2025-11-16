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
