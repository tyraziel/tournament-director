#!/bin/bash

# Database Availability Checker
# AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0

echo "==================================================================="
echo "         Tournament Director - Database Availability Check"
echo "==================================================================="
echo ""

# Check SQLite
echo "📦 SQLite:"
if python3 -c "import sqlite3; print(f'   ✅ Available (version {sqlite3.version})')" 2>/dev/null; then
    echo "   📊 In-memory testing: Ready"
else
    echo "   ❌ Not available"
fi
echo ""

# Check PostgreSQL
echo "🐘 PostgreSQL:"
if pgrep -f postgres > /dev/null 2>&1; then
    PG_VERSION=$(su - postgres -c "/usr/lib/postgresql/16/bin/psql --version 2>/dev/null" | head -1 || echo "Unknown version")
    echo "   ✅ Server running: $PG_VERSION"
    if su - postgres -c "psql -h /tmp/pg_socket -lqt 2>/dev/null" | cut -d \| -f 1 | grep -qw tournament_director; then
        echo "   ✅ Database 'tournament_director' exists"
    else
        echo "   ⚠️  Database 'tournament_director' not found"
        echo "   💡 Create with: su - postgres -c \"psql -h /tmp/pg_socket -c 'CREATE DATABASE tournament_director;'\""
    fi
else
    echo "   ❌ Server not running"
    echo "   💡 Start with: See DATABASE_TESTING_SETUP.md section 2"
fi
echo ""

# Check MySQL
echo "🐬 MySQL:"
if pgrep -f mysqld > /dev/null 2>&1; then
    MYSQL_VERSION=$(mysqld --version 2>/dev/null || echo "Unknown version")
    echo "   ✅ Server running: $MYSQL_VERSION"
    if mysql -u test -ptest123 -e "USE tournament_director;" 2>/dev/null; then
        echo "   ✅ Database 'tournament_director' accessible"
    else
        echo "   ⚠️  Database or credentials not configured"
        echo "   💡 Setup: See DATABASE_TESTING_SETUP.md section 3"
    fi
else
    echo "   ❌ Server not running"
    echo "   💡 Install: sudo apt-get install mysql-server"
fi
echo ""

# Check MariaDB
echo "🦭 MariaDB:"
if pgrep -f mariadbd > /dev/null 2>&1; then
    MARIADB_VERSION=$(mariadbd --version 2>/dev/null || echo "Unknown version")
    echo "   ✅ Server running: $MARIADB_VERSION"
    if mysql -u test -ptest123 -e "USE tournament_director;" 2>/dev/null; then
        echo "   ✅ Database 'tournament_director' accessible"
    else
        echo "   ⚠️  Database or credentials not configured"
        echo "   💡 Setup: See DATABASE_TESTING_SETUP.md section 4"
    fi
else
    echo "   ❌ Server not running"
    echo "   💡 Install: sudo apt-get install mariadb-server"
fi
echo ""

echo "==================================================================="
echo "                     Python Database Drivers"
echo "==================================================================="
echo ""

# Check aiosqlite
if python3 -c "import aiosqlite" 2>/dev/null; then
    VERSION=$(python3 -c "import aiosqlite; print(aiosqlite.__version__)" 2>/dev/null || echo "unknown")
    echo "✅ aiosqlite==$VERSION"
else
    echo "❌ aiosqlite not installed"
    echo "   💡 Install: pip install aiosqlite==0.20.0"
fi

# Check asyncpg
if python3 -c "import asyncpg" 2>/dev/null; then
    VERSION=$(python3 -c "import asyncpg; print(asyncpg.__version__)" 2>/dev/null || echo "unknown")
    echo "✅ asyncpg==$VERSION"
else
    echo "❌ asyncpg not installed"
    echo "   💡 Install: pip install asyncpg==0.29.0"
fi

# Check aiomysql
if python3 -c "import aiomysql" 2>/dev/null; then
    VERSION=$(python3 -c "import aiomysql; print(aiomysql.__version__)" 2>/dev/null || echo "unknown")
    echo "✅ aiomysql==$VERSION"
else
    echo "❌ aiomysql not installed"
    echo "   💡 Install: pip install aiomysql==0.2.0"
fi

echo ""
echo "==================================================================="
echo "                         Test Status"
echo "==================================================================="
echo ""

# Count available databases
AVAILABLE=0
TOTAL=4

if python3 -c "import sqlite3" 2>/dev/null; then
    AVAILABLE=$((AVAILABLE + 1))
    echo "✅ SQLite: Ready for testing (23 tests)"
fi

if pgrep -f postgres > /dev/null 2>&1; then
    AVAILABLE=$((AVAILABLE + 1))
    echo "✅ PostgreSQL: Ready for testing (23 tests)"
fi

if pgrep -f mysqld > /dev/null 2>&1; then
    AVAILABLE=$((AVAILABLE + 1))
    echo "✅ MySQL: Ready for testing (23 tests)"
else
    echo "⏸️  MySQL: Not available (23 tests pending)"
fi

if pgrep -f mariadbd > /dev/null 2>&1; then
    AVAILABLE=$((AVAILABLE + 1))
    echo "✅ MariaDB: Ready for testing (23 tests)"
else
    echo "⏸️  MariaDB: Not available (23 tests pending)"
fi

echo ""
TESTED=$((AVAILABLE * 23))
POTENTIAL=$((TOTAL * 23))
PERCENTAGE=$((TESTED * 100 / POTENTIAL))

echo "📊 Test Coverage: $TESTED/$POTENTIAL tests ($PERCENTAGE%)"
echo "   - Databases available: $AVAILABLE/$TOTAL"
echo "   - Tests per database: 23"
echo ""

if [ $AVAILABLE -eq $TOTAL ]; then
    echo "🎉 All databases available! Run: pytest tests/test_database_backend.py -v"
else
    echo "💡 Install missing databases to reach 100% coverage"
    echo "   See: DATABASE_TESTING_SETUP.md"
fi

echo ""
echo "==================================================================="
