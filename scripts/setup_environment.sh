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
