"""Tests for database backend implementation.

Tests all CRUD operations across SQLite, PostgreSQL, MySQL, and MariaDB.
Follows TDD Red-Green-Refactor methodology.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4

from src.data.database import DatabaseDataLayer
from src.data.exceptions import NotFoundError, DuplicateError
from src.models.player import Player
from src.models.venue import Venue
from src.models.format import Format
from src.models.base import GameSystem, BaseFormat
from src.models.tournament import Tournament, TournamentRegistration, RegistrationControl
from src.models.base import TournamentStatus, TournamentVisibility, PlayerStatus


# Database URL fixtures for different databases
@pytest.fixture(params=["sqlite"])  # Start with SQLite only
def database_url(request):
    """Provide database URLs for testing.

    Initially tests SQLite only. Add PostgreSQL, MySQL, MariaDB after SQLite passes.
    """
    if request.param == "sqlite":
        # Use in-memory SQLite for fast testing
        return "sqlite+aiosqlite:///:memory:"
    # TODO: Add after SQLite tests pass
    # elif request.param == "postgresql":
    #     return "postgresql+asyncpg://test:test@localhost/test_tournament_director"
    # elif request.param == "mysql":
    #     return "mysql+aiomysql://test:test@localhost/test_tournament_director"
    # elif request.param == "mariadb":
    #     return "mariadb+aiomysql://test:test@localhost/test_tournament_director"


@pytest_asyncio.fixture
async def data_layer(database_url):
    """Create and initialize a database data layer for testing."""
    dl = DatabaseDataLayer(database_url)
    await dl.initialize()

    yield dl

    # Cleanup
    await dl.close()


@pytest_asyncio.fixture
async def clean_data_layer(database_url):
    """Create a fresh database for each test."""
    dl = DatabaseDataLayer(database_url)
    await dl.initialize()
    await dl.clear_all_data()

    yield dl

    await dl.close()


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.asyncio
async def test_database_health_check(data_layer):
    """Test database health check returns healthy status."""
    health = await data_layer.health_check()

    assert health["status"] == "healthy"
    assert health["connection"] == "active"


@pytest.mark.asyncio
async def test_database_initialization(database_url):
    """Test database initializes correctly."""
    dl = DatabaseDataLayer(database_url)

    # Should raise error if not initialized
    with pytest.raises(RuntimeError, match="not initialized"):
        _ = dl.players

    # Initialize
    await dl.initialize()

    # Should work after initialization
    assert dl.players is not None
    assert dl.venues is not None
    assert dl.formats is not None
    assert dl.tournaments is not None

    await dl.close()


# ============================================================================
# Player Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_player_create(clean_data_layer):
    """Test creating a player."""
    player = Player(
        id=uuid4(),
        name="Alice",
        discord_id="alice#1234",
        email="alice@example.com",
        created_at=datetime.now(timezone.utc)
    )

    created = await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    assert created.id == player.id
    assert created.name == "Alice"
    assert created.discord_id == "alice#1234"


@pytest.mark.asyncio
async def test_player_get_by_id(clean_data_layer):
    """Test retrieving a player by ID."""
    player = Player(
        id=uuid4(),
        name="Bob",
        created_at=datetime.now(timezone.utc)
    )

    await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    retrieved = await clean_data_layer.players.get_by_id(player.id)

    assert retrieved.id == player.id
    assert retrieved.name == "Bob"


@pytest.mark.asyncio
async def test_player_get_by_id_not_found(clean_data_layer):
    """Test retrieving non-existent player raises NotFoundError."""
    fake_id = uuid4()

    with pytest.raises(NotFoundError):
        await clean_data_layer.players.get_by_id(fake_id)


@pytest.mark.asyncio
async def test_player_duplicate_id(clean_data_layer):
    """Test creating player with duplicate ID raises DuplicateError."""
    player_id = uuid4()

    player1 = Player(id=player_id, name="Alice", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player1)
    await clean_data_layer.commit()

    player2 = Player(id=player_id, name="Bob", created_at=datetime.now(timezone.utc))

    with pytest.raises(DuplicateError):
        await clean_data_layer.players.create(player2)


@pytest.mark.asyncio
async def test_player_duplicate_discord_id(clean_data_layer):
    """Test creating player with duplicate Discord ID raises DuplicateError."""
    player1 = Player(
        id=uuid4(),
        name="Alice",
        discord_id="alice#1234",
        created_at=datetime.now(timezone.utc)
    )
    await clean_data_layer.players.create(player1)
    await clean_data_layer.commit()

    player2 = Player(
        id=uuid4(),
        name="Bob",
        discord_id="alice#1234",  # Same Discord ID
        created_at=datetime.now(timezone.utc)
    )

    with pytest.raises(DuplicateError):
        await clean_data_layer.players.create(player2)


@pytest.mark.asyncio
async def test_player_get_by_name(clean_data_layer):
    """Test retrieving player by name."""
    player = Player(id=uuid4(), name="Charlie", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    retrieved = await clean_data_layer.players.get_by_name("Charlie")

    assert retrieved is not None
    assert retrieved.name == "Charlie"


@pytest.mark.asyncio
async def test_player_get_by_discord_id(clean_data_layer):
    """Test retrieving player by Discord ID."""
    player = Player(
        id=uuid4(),
        name="Dave",
        discord_id="dave#5678",
        created_at=datetime.now(timezone.utc)
    )
    await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    retrieved = await clean_data_layer.players.get_by_discord_id("dave#5678")

    assert retrieved is not None
    assert retrieved.discord_id == "dave#5678"


@pytest.mark.asyncio
async def test_player_list_all(clean_data_layer):
    """Test listing all players."""
    players = [
        Player(id=uuid4(), name=f"Player{i}", created_at=datetime.now(timezone.utc))
        for i in range(5)
    ]

    for player in players:
        await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    all_players = await clean_data_layer.players.list_all()

    assert len(all_players) == 5


@pytest.mark.asyncio
async def test_player_list_with_pagination(clean_data_layer):
    """Test listing players with limit and offset."""
    players = [
        Player(id=uuid4(), name=f"Player{i}", created_at=datetime.now(timezone.utc))
        for i in range(10)
    ]

    for player in players:
        await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    # Get first 3
    page1 = await clean_data_layer.players.list_all(limit=3, offset=0)
    assert len(page1) == 3

    # Get next 3
    page2 = await clean_data_layer.players.list_all(limit=3, offset=3)
    assert len(page2) == 3

    # Ensure different players
    assert page1[0].id != page2[0].id


@pytest.mark.asyncio
async def test_player_update(clean_data_layer):
    """Test updating a player."""
    player = Player(id=uuid4(), name="Eve", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    # Update player
    player.name = "Eve Updated"
    player.email = "eve@example.com"

    updated = await clean_data_layer.players.update(player)
    await clean_data_layer.commit()

    # Verify update
    retrieved = await clean_data_layer.players.get_by_id(player.id)
    assert retrieved.name == "Eve Updated"
    assert retrieved.email == "eve@example.com"


@pytest.mark.asyncio
async def test_player_delete(clean_data_layer):
    """Test deleting a player."""
    player = Player(id=uuid4(), name="Frank", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)
    await clean_data_layer.commit()

    # Delete player
    await clean_data_layer.players.delete(player.id)
    await clean_data_layer.commit()

    # Verify deletion
    with pytest.raises(NotFoundError):
        await clean_data_layer.players.get_by_id(player.id)


# ============================================================================
# Venue Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_venue_create(clean_data_layer):
    """Test creating a venue."""
    venue = Venue(
        id=uuid4(),
        name="Kitchen Table",
        address="123 Main St",
        description="Casual kitchen table gaming"
    )

    created = await clean_data_layer.venues.create(venue)
    await clean_data_layer.commit()

    assert created.id == venue.id
    assert created.name == "Kitchen Table"


@pytest.mark.asyncio
async def test_venue_get_by_name(clean_data_layer):
    """Test retrieving venue by name."""
    venue = Venue(id=uuid4(), name="Snack House")
    await clean_data_layer.venues.create(venue)
    await clean_data_layer.commit()

    retrieved = await clean_data_layer.venues.get_by_name("Snack House")

    assert retrieved is not None
    assert retrieved.name == "Snack House"


# ============================================================================
# Format Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_format_create(clean_data_layer):
    """Test creating a format."""
    fmt = Format(
        id=uuid4(),
        name="Pauper",
        game_system=GameSystem.MTG,
        base_format=BaseFormat.CONSTRUCTED,
        card_pool="Commons only",
        match_structure="BO3"
    )

    created = await clean_data_layer.formats.create(fmt)
    await clean_data_layer.commit()

    assert created.id == fmt.id
    assert created.name == "Pauper"
    assert created.game_system == GameSystem.MTG


@pytest.mark.asyncio
async def test_format_list_by_game_system(clean_data_layer):
    """Test listing formats by game system."""
    formats = [
        Format(
            id=uuid4(),
            name="Pauper",
            game_system=GameSystem.MTG,
            base_format=BaseFormat.CONSTRUCTED,
            card_pool="Commons only"
        ),
        Format(
            id=uuid4(),
            name="Standard",
            game_system=GameSystem.MTG,
            base_format=BaseFormat.CONSTRUCTED,
            card_pool="Standard legal"
        ),
        Format(
            id=uuid4(),
            name="Unlimited",
            game_system=GameSystem.POKEMON,
            base_format=BaseFormat.CONSTRUCTED,
            card_pool="All cards"
        ),
    ]

    for fmt in formats:
        await clean_data_layer.formats.create(fmt)
    await clean_data_layer.commit()

    mtg_formats = await clean_data_layer.formats.list_by_game_system(GameSystem.MTG.value)

    assert len(mtg_formats) == 2
    assert all(f.game_system == GameSystem.MTG for f in mtg_formats)


# ============================================================================
# Tournament Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_tournament_create(clean_data_layer):
    """Test creating a tournament with RegistrationControl."""
    # Create dependencies
    player = Player(id=uuid4(), name="TO Player", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)

    venue = Venue(id=uuid4(), name="Test Venue")
    await clean_data_layer.venues.create(venue)

    fmt = Format(
        id=uuid4(),
        name="Pauper",
        game_system=GameSystem.MTG,
        base_format=BaseFormat.CONSTRUCTED,
        card_pool="Commons only"
    )
    await clean_data_layer.formats.create(fmt)
    await clean_data_layer.commit()

    # Create tournament
    tournament = Tournament(
        id=uuid4(),
        name="Kitchen Table Pauper",
        status=TournamentStatus.DRAFT,
        visibility=TournamentVisibility.PUBLIC,
        registration=RegistrationControl(max_players=8),
        format_id=fmt.id,
        venue_id=venue.id,
        created_by=player.id,
        created_at=datetime.now(timezone.utc)
    )

    created = await clean_data_layer.tournaments.create(tournament)
    await clean_data_layer.commit()

    assert created.id == tournament.id
    assert created.name == "Kitchen Table Pauper"
    assert created.registration.max_players == 8


@pytest.mark.asyncio
async def test_tournament_list_by_status(clean_data_layer):
    """Test listing tournaments by status."""
    # Create dependencies
    player = Player(id=uuid4(), name="TO", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)

    venue = Venue(id=uuid4(), name="Venue")
    await clean_data_layer.venues.create(venue)

    fmt = Format(
        id=uuid4(),
        name="Format",
        game_system=GameSystem.MTG,
        base_format=BaseFormat.CONSTRUCTED,
        card_pool="All"
    )
    await clean_data_layer.formats.create(fmt)
    await clean_data_layer.commit()

    # Create tournaments with different statuses
    tournaments = [
        Tournament(
            id=uuid4(),
            name=f"Tournament {i}",
            status=TournamentStatus.DRAFT if i < 2 else TournamentStatus.IN_PROGRESS,
            visibility=TournamentVisibility.PUBLIC,
            registration=RegistrationControl(),
            format_id=fmt.id,
            venue_id=venue.id,
            created_by=player.id,
            created_at=datetime.now(timezone.utc)
        )
        for i in range(4)
    ]

    for t in tournaments:
        await clean_data_layer.tournaments.create(t)
    await clean_data_layer.commit()

    draft_tournaments = await clean_data_layer.tournaments.list_by_status(TournamentStatus.DRAFT.value)

    assert len(draft_tournaments) == 2


# ============================================================================
# Registration Repository Tests
# ============================================================================

@pytest.mark.asyncio
async def test_registration_create(clean_data_layer):
    """Test creating a tournament registration."""
    # Create dependencies
    player = Player(id=uuid4(), name="Player1", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)

    to_player = Player(id=uuid4(), name="TO", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(to_player)

    venue = Venue(id=uuid4(), name="Venue")
    await clean_data_layer.venues.create(venue)

    fmt = Format(
        id=uuid4(),
        name="Format",
        game_system=GameSystem.MTG,
        base_format=BaseFormat.CONSTRUCTED,
        card_pool="All"
    )
    await clean_data_layer.formats.create(fmt)

    tournament = Tournament(
        id=uuid4(),
        name="Tournament",
        status=TournamentStatus.REGISTRATION_OPEN,
        visibility=TournamentVisibility.PUBLIC,
        registration=RegistrationControl(),
        format_id=fmt.id,
        venue_id=venue.id,
        created_by=to_player.id,
        created_at=datetime.now(timezone.utc)
    )
    await clean_data_layer.tournaments.create(tournament)
    await clean_data_layer.commit()

    # Create registration
    reg = TournamentRegistration(
        id=uuid4(),
        tournament_id=tournament.id,
        player_id=player.id,
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
        registration_time=datetime.now(timezone.utc)
    )

    created = await clean_data_layer.registrations.create(reg)
    await clean_data_layer.commit()

    assert created.id == reg.id
    assert created.sequence_id == 1


@pytest.mark.asyncio
async def test_registration_get_next_sequence_id(clean_data_layer):
    """Test getting next sequence ID for tournament."""
    # Create dependencies
    player1 = Player(id=uuid4(), name="Player1", created_at=datetime.now(timezone.utc))
    player2 = Player(id=uuid4(), name="Player2", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player1)
    await clean_data_layer.players.create(player2)

    to_player = Player(id=uuid4(), name="TO", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(to_player)

    venue = Venue(id=uuid4(), name="Venue")
    await clean_data_layer.venues.create(venue)

    fmt = Format(
        id=uuid4(),
        name="Format",
        game_system=GameSystem.MTG,
        base_format=BaseFormat.CONSTRUCTED,
        card_pool="All"
    )
    await clean_data_layer.formats.create(fmt)

    tournament = Tournament(
        id=uuid4(),
        name="Tournament",
        status=TournamentStatus.REGISTRATION_OPEN,
        visibility=TournamentVisibility.PUBLIC,
        registration=RegistrationControl(),
        format_id=fmt.id,
        venue_id=venue.id,
        created_by=to_player.id,
        created_at=datetime.now(timezone.utc)
    )
    await clean_data_layer.tournaments.create(tournament)
    await clean_data_layer.commit()

    # First sequence ID should be 1
    next_id = await clean_data_layer.registrations.get_next_sequence_id(tournament.id)
    assert next_id == 1

    # Create a registration
    reg1 = TournamentRegistration(
        id=uuid4(),
        tournament_id=tournament.id,
        player_id=player1.id,
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
        registration_time=datetime.now(timezone.utc)
    )
    await clean_data_layer.registrations.create(reg1)
    await clean_data_layer.commit()

    # Next sequence ID should be 2
    next_id = await clean_data_layer.registrations.get_next_sequence_id(tournament.id)
    assert next_id == 2


@pytest.mark.asyncio
async def test_registration_duplicate_player(clean_data_layer):
    """Test that duplicate player registration raises DuplicateError."""
    # Create dependencies
    player = Player(id=uuid4(), name="Player1", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(player)

    to_player = Player(id=uuid4(), name="TO", created_at=datetime.now(timezone.utc))
    await clean_data_layer.players.create(to_player)

    venue = Venue(id=uuid4(), name="Venue")
    await clean_data_layer.venues.create(venue)

    fmt = Format(
        id=uuid4(),
        name="Format",
        game_system=GameSystem.MTG,
        base_format=BaseFormat.CONSTRUCTED,
        card_pool="All"
    )
    await clean_data_layer.formats.create(fmt)

    tournament = Tournament(
        id=uuid4(),
        name="Tournament",
        status=TournamentStatus.REGISTRATION_OPEN,
        visibility=TournamentVisibility.PUBLIC,
        registration=RegistrationControl(),
        format_id=fmt.id,
        venue_id=venue.id,
        created_by=to_player.id,
        created_at=datetime.now(timezone.utc)
    )
    await clean_data_layer.tournaments.create(tournament)
    await clean_data_layer.commit()

    # Create first registration
    reg1 = TournamentRegistration(
        id=uuid4(),
        tournament_id=tournament.id,
        player_id=player.id,
        sequence_id=1,
        status=PlayerStatus.ACTIVE,
        registration_time=datetime.now(timezone.utc)
    )
    await clean_data_layer.registrations.create(reg1)
    await clean_data_layer.commit()

    # Try to register same player again
    reg2 = TournamentRegistration(
        id=uuid4(),
        tournament_id=tournament.id,
        player_id=player.id,  # Same player!
        sequence_id=2,
        status=PlayerStatus.ACTIVE,
        registration_time=datetime.now(timezone.utc)
    )

    with pytest.raises(DuplicateError):
        await clean_data_layer.registrations.create(reg2)


# ============================================================================
# Seed Data Test
# ============================================================================

@pytest.mark.asyncio
async def test_seed_data(clean_data_layer):
    """Test seeding data from dictionary."""
    seed_data = {
        "players": [
            {
                "id": uuid4(),
                "name": "Alice",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": uuid4(),
                "name": "Bob",
                "created_at": datetime.now(timezone.utc)
            }
        ],
        "venues": [
            {
                "id": uuid4(),
                "name": "Kitchen Table"
            }
        ]
    }

    await clean_data_layer.seed_data(seed_data)

    # Verify seeded data
    players = await clean_data_layer.players.list_all()
    assert len(players) == 2

    venues = await clean_data_layer.venues.list_all()
    assert len(venues) == 1
