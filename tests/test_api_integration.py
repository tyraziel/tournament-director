"""
API integration tests for all endpoints.

Tests complete CRUD workflows using httpx TestClient.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.api.main import app
from src.models.base import GameSystem, BaseFormat


@pytest_asyncio.fixture
async def client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test basic health check."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "Tournament Director API"

    @pytest.mark.asyncio
    async def test_detailed_health_check(self, client: AsyncClient):
        """Test detailed health check with data layer validation."""
        response = await client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
        assert data["components"]["api"] == "healthy"
        assert "data_layer" in data["components"]

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns API information."""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Tournament Director API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"
        assert data["openapi"] == "/openapi.json"


class TestPlayerEndpoints:
    """Test player CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_player(self, client: AsyncClient):
        """Test creating a new player."""
        player_data = {
            "name": "Alice Johnson",
            "discord_id": "alice#1234",
            "email": "alice@example.com"
        }

        response = await client.post("/players/", json=player_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["name"] == "Alice Johnson"
        assert data["discord_id"] == "alice#1234"
        assert data["email"] == "alice@example.com"

    @pytest.mark.asyncio
    async def test_list_players(self, client: AsyncClient):
        """Test listing all players."""
        # Create a player first
        await client.post("/players/", json={"name": "Bob"})

        response = await client.get("/players/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_player_by_id(self, client: AsyncClient):
        """Test retrieving a player by ID."""
        # Create a player
        create_response = await client.post("/players/", json={"name": "Charlie"})
        player_id = create_response.json()["id"]

        # Get the player
        response = await client.get(f"/players/{player_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == player_id
        assert data["name"] == "Charlie"

    @pytest.mark.asyncio
    async def test_get_player_not_found(self, client: AsyncClient):
        """Test getting a non-existent player returns 404."""
        fake_id = str(uuid4())
        response = await client.get(f"/players/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_player(self, client: AsyncClient):
        """Test updating a player."""
        # Create a player
        create_response = await client.post("/players/", json={"name": "Diana"})
        player_id = create_response.json()["id"]

        # Update the player
        update_data = {"name": "Diana Prince"}
        response = await client.put(f"/players/{player_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Diana Prince"

    @pytest.mark.asyncio
    async def test_delete_player(self, client: AsyncClient):
        """Test deleting a player."""
        # Create a player
        create_response = await client.post("/players/", json={"name": "Eve"})
        player_id = create_response.json()["id"]

        # Delete the player
        response = await client.delete(f"/players/{player_id}")
        assert response.status_code == 204

        # Verify player is gone
        get_response = await client.get(f"/players/{player_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_search_players_by_name(self, client: AsyncClient):
        """Test searching players by name."""
        # Create players with similar names
        await client.post("/players/", json={"name": "Frank Miller"})
        await client.post("/players/", json={"name": "Frank Castle"})
        await client.post("/players/", json={"name": "George"})

        # Search for "Frank"
        response = await client.get("/players/search/by-name", params={"name": "Frank"})
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 2
        assert all("Frank" in player["name"] for player in data)

    @pytest.mark.asyncio
    async def test_get_player_by_discord_id(self, client: AsyncClient):
        """Test getting a player by Discord ID."""
        import urllib.parse

        # Create a player with Discord ID
        discord_id = "user#9999"
        create_response = await client.post(
            "/players/",
            json={"name": "Discord User", "discord_id": discord_id}
        )
        assert create_response.status_code == 201

        # Get by Discord ID (URL encode the # symbol)
        encoded_discord_id = urllib.parse.quote(discord_id, safe='')
        response = await client.get(f"/players/discord/{encoded_discord_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["discord_id"] == discord_id

    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient):
        """Test pagination parameters."""
        # Create multiple players
        for i in range(5):
            await client.post("/players/", json={"name": f"Player {i}"})

        # Test with limit
        response = await client.get("/players/", params={"limit": 2})
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Test with offset
        response = await client.get("/players/", params={"limit": 2, "offset": 2})
        assert response.status_code == 200


class TestVenueEndpoints:
    """Test venue CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_venue(self, client: AsyncClient):
        """Test creating a new venue."""
        venue_data = {
            "name": "Kitchen Table",
            "address": "123 Main St",
            "description": "Casual gaming venue"
        }

        response = await client.post("/venues/", json=venue_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["name"] == "Kitchen Table"
        assert data["address"] == "123 Main St"

    @pytest.mark.asyncio
    async def test_list_venues(self, client: AsyncClient):
        """Test listing all venues."""
        response = await client.get("/venues/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_venue_by_id(self, client: AsyncClient):
        """Test retrieving a venue by ID."""
        create_response = await client.post("/venues/", json={"name": "Snack House"})
        venue_id = create_response.json()["id"]

        response = await client.get(f"/venues/{venue_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Snack House"

    @pytest.mark.asyncio
    async def test_update_venue(self, client: AsyncClient):
        """Test updating a venue."""
        create_response = await client.post("/venues/", json={"name": "Old Name"})
        venue_id = create_response.json()["id"]

        response = await client.put(
            f"/venues/{venue_id}",
            json={"name": "New Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_delete_venue(self, client: AsyncClient):
        """Test deleting a venue."""
        create_response = await client.post("/venues/", json={"name": "Temporary"})
        venue_id = create_response.json()["id"]

        response = await client.delete(f"/venues/{venue_id}")
        assert response.status_code == 204


class TestFormatEndpoints:
    """Test format CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_format(self, client: AsyncClient):
        """Test creating a new format."""
        format_data = {
            "name": "Pauper",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Pauper",
            "match_structure": "BO3",
            "description": "Commons only format"
        }

        response = await client.post("/formats/", json=format_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Pauper"
        assert data["game_system"] == "magic_the_gathering"

    @pytest.mark.asyncio
    async def test_list_formats(self, client: AsyncClient):
        """Test listing all formats."""
        response = await client.get("/formats/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_list_formats_by_game_system(self, client: AsyncClient):
        """Test filtering formats by game system."""
        # Create MTG format
        await client.post("/formats/", json={
            "name": "Standard",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Standard"
        })

        # Create Pokemon format
        await client.post("/formats/", json={
            "name": "Standard",
            "game_system": "pokemon",
            "base_format": "constructed",
            "card_pool": "Standard"
        })

        # Get only MTG formats
        response = await client.get("/formats/game/magic_the_gathering")
        assert response.status_code == 200

        data = response.json()
        assert all(f["game_system"] == "magic_the_gathering" for f in data)

    @pytest.mark.asyncio
    async def test_get_format_by_id(self, client: AsyncClient):
        """Test retrieving a format by ID."""
        create_response = await client.post("/formats/", json={
            "name": "Limited",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "card_pool": "Current Set"
        })
        format_id = create_response.json()["id"]

        response = await client.get(f"/formats/{format_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Limited"

    @pytest.mark.asyncio
    async def test_update_format(self, client: AsyncClient):
        """Test updating a format."""
        create_response = await client.post("/formats/", json={
            "name": "Modern",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Modern"
        })
        format_id = create_response.json()["id"]

        response = await client.put(
            f"/formats/{format_id}",
            json={"description": "Updated description"}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_format(self, client: AsyncClient):
        """Test deleting a format."""
        create_response = await client.post("/formats/", json={
            "name": "Temporary",
            "game_system": "custom_tcg",
            "base_format": "special",
            "card_pool": "Custom"
        })
        format_id = create_response.json()["id"]

        response = await client.delete(f"/formats/{format_id}")
        assert response.status_code == 204


class TestValidationErrors:
    """Test request validation and error responses."""

    @pytest.mark.asyncio
    async def test_invalid_player_name(self, client: AsyncClient):
        """Test creating a player with invalid name."""
        response = await client.post("/players/", json={"name": ""})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_invalid_uuid(self, client: AsyncClient):
        """Test using invalid UUID format."""
        response = await client.get("/players/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_game_system(self, client: AsyncClient):
        """Test creating format with invalid game system."""
        response = await client.post("/formats/", json={
            "name": "Test",
            "game_system": "invalid_system",
            "base_format": "constructed",
            "card_pool": "Test"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client: AsyncClient):
        """Test creating player without required fields."""
        response = await client.post("/players/", json={})
        assert response.status_code == 422


class TestTournamentEndpoints:
    """Test tournament CRUD and lifecycle endpoints."""

    @pytest.mark.asyncio
    async def test_create_tournament(self, client: AsyncClient):
        """Test creating a new tournament."""
        # First create dependencies (player, venue, format)
        player_response = await client.post("/players/", json={"name": "Tournament Organizer"})
        player_id = player_response.json()["id"]

        venue_response = await client.post("/venues/", json={
            "name": "Test Game Store",
            "address": "123 Main St"
        })
        venue_id = venue_response.json()["id"]

        format_response = await client.post("/formats/", json={
            "name": "Pauper for Tournament Create Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Common only"
        })
        format_id = format_response.json()["id"]

        # Now create tournament
        tournament_data = {
            "name": "Weekly Pauper",
            "format_id": format_id,
            "venue_id": venue_id,
            "created_by": player_id,
            "visibility": "public",
            "description": "Weekly Pauper tournament",
            "max_players": 16
        }

        response = await client.post("/tournaments/", json=tournament_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["name"] == "Weekly Pauper"
        assert data["status"] == "draft"
        assert data["visibility"] == "public"
        assert data["registration"]["max_players"] == 16

    @pytest.mark.asyncio
    async def test_list_tournaments(self, client: AsyncClient):
        """Test listing all tournaments."""
        response = await client.get("/tournaments/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_tournament_by_id(self, client: AsyncClient):
        """Test getting a specific tournament by ID."""
        # Create tournament first
        player_response = await client.post("/players/", json={"name": "TO"})
        venue_response = await client.post("/venues/", json={"name": "Store", "address": "123 St"})
        format_response = await client.post("/formats/", json={
            "name": "Format",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "All"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Test Tournament",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Get tournament
        response = await client.get(f"/tournaments/{tournament_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == tournament_id
        assert data["name"] == "Test Tournament"

    @pytest.mark.asyncio
    async def test_get_tournament_not_found(self, client: AsyncClient):
        """Test getting a non-existent tournament."""
        fake_id = str(uuid4())
        response = await client.get(f"/tournaments/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_tournament(self, client: AsyncClient):
        """Test updating a tournament."""
        # Create tournament first
        player_response = await client.post("/players/", json={"name": "TO Update Test"})
        venue_response = await client.post("/venues/", json={"name": "Store Update", "address": "123 St"})
        format_response = await client.post("/formats/", json={
            "name": "Format for Update Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "All"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Original Name",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Update tournament
        response = await client.put(
            f"/tournaments/{tournament_id}",
            json={"name": "Updated Name", "description": "Updated description"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_tournament(self, client: AsyncClient):
        """Test deleting a tournament."""
        # Create tournament first
        player_response = await client.post("/players/", json={"name": "TO Delete Test"})
        venue_response = await client.post("/venues/", json={"name": "Store Delete", "address": "123 St"})
        format_response = await client.post("/formats/", json={
            "name": "Format for Delete Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "All"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "To Delete",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Delete tournament
        response = await client.delete(f"/tournaments/{tournament_id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_list_tournaments_by_status(self, client: AsyncClient):
        """Test filtering tournaments by status."""
        response = await client.get("/tournaments/status/draft")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # All returned tournaments should have DRAFT status
        for tournament in data:
            assert tournament["status"] == "draft"

    @pytest.mark.asyncio
    async def test_list_tournaments_by_venue(self, client: AsyncClient):
        """Test filtering tournaments by venue."""
        # Create venue
        venue_response = await client.post("/venues/", json={
            "name": "Specific Store",
            "address": "456 Main St"
        })
        venue_id = venue_response.json()["id"]

        # Query by venue
        response = await client.get(f"/tournaments/venue/{venue_id}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_tournaments_by_format(self, client: AsyncClient):
        """Test filtering tournaments by format."""
        # Create format
        format_response = await client.post("/formats/", json={
            "name": "Specific Format",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Test"
        })
        format_id = format_response.json()["id"]

        # Query by format
        response = await client.get(f"/tournaments/format/{format_id}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_start_tournament(self, client: AsyncClient):
        """Test starting a tournament."""
        # Create tournament with registrations
        player_response = await client.post("/players/", json={"name": "TO Start Test"})
        venue_response = await client.post("/venues/", json={"name": "Store Start", "address": "123 St"})
        format_response = await client.post("/formats/", json={
            "name": "Format for Start Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "All"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "To Start",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Register at least 2 players for tournament to start
        # This will be tested more thoroughly once registration endpoints exist
        # For now, we expect this to fail with "need at least 2 players" error

        response = await client.post(f"/tournaments/{tournament_id}/start")
        # Should fail with 400 because no players registered
        assert response.status_code == 400
        assert "at least 2 players" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_complete_tournament(self, client: AsyncClient):
        """Test completing a tournament."""
        # Create tournament
        player_response = await client.post("/players/", json={"name": "TO Complete Test"})
        venue_response = await client.post("/venues/", json={"name": "Store Complete", "address": "123 St"})
        format_response = await client.post("/formats/", json={
            "name": "Format for Complete Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "All"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "To Complete",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Try to complete tournament (should fail - no components, was never started)
        response = await client.post(f"/tournaments/{tournament_id}/complete")
        assert response.status_code == 400
        assert "no components" in response.json()["detail"]


class TestRegistrationEndpoints:
    """Test registration endpoints.

    AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
    """

    @pytest.mark.asyncio
    async def test_register_player_success(self, client: AsyncClient):
        """Test successfully registering a player to a tournament."""
        # Create dependencies
        player_response = await client.post("/players/", json={"name": "Alice"})
        player_id = player_response.json()["id"]

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Registration Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Pauper for Registration Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Common only"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Weekly Pauper Registration Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_id
        })
        tournament_id = tournament_response.json()["id"]

        # Register player
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player_id}
        )
        assert response.status_code == 201

        data = response.json()
        assert data["tournament_id"] == tournament_id
        assert data["player_id"] == player_id
        assert data["sequence_id"] == 1  # First player
        assert data["status"] == "active"
        assert "registration_time" in data

    @pytest.mark.asyncio
    async def test_register_player_with_password(self, client: AsyncClient):
        """Test registering player to password-protected tournament."""
        # Create dependencies
        player_response = await client.post("/players/", json={"name": "Bob Password Test"})
        player_id = player_response.json()["id"]

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Password Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Modern for Registration Password Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Modern legal cards"
        })

        # Create password-protected tournament
        tournament_response = await client.post("/tournaments/", json={
            "name": "Password Protected Tournament",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_id,
            "registration_password": "secret123"
        })
        tournament_id = tournament_response.json()["id"]

        # Register with correct password
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player_id, "password": "secret123"}
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_player_wrong_password(self, client: AsyncClient):
        """Test registration fails with wrong password."""
        # Create dependencies
        player_response = await client.post("/players/", json={"name": "Charlie Wrong Password Test"})
        player_id = player_response.json()["id"]

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Wrong Password Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Standard for Registration Wrong Password Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Standard legal cards"
        })

        # Create password-protected tournament
        tournament_response = await client.post("/tournaments/", json={
            "name": "Password Protected Tournament 2",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_id,
            "registration_password": "correct_password"
        })
        tournament_id = tournament_response.json()["id"]

        # Try to register with wrong password
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player_id, "password": "wrong_password"}
        )
        assert response.status_code == 403
        assert "password" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_player_duplicate(self, client: AsyncClient):
        """Test that duplicate registration is prevented."""
        # Create dependencies
        player_response = await client.post("/players/", json={"name": "Diana"})
        player_id = player_response.json()["id"]

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Duplicate Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Legacy for Registration Duplicate Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Legacy legal cards"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Duplicate Registration Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_id
        })
        tournament_id = tournament_response.json()["id"]

        # First registration - should succeed
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player_id}
        )
        assert response.status_code == 201

        # Duplicate registration - should fail
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player_id}
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_player_tournament_not_found(self, client: AsyncClient):
        """Test registration to non-existent tournament."""
        player_response = await client.post("/players/", json={"name": "Eve"})
        player_id = player_response.json()["id"]

        fake_tournament_id = str(uuid4())
        response = await client.post(
            f"/tournaments/{fake_tournament_id}/register",
            json={"player_id": player_id}
        )
        assert response.status_code == 404
        assert "tournament" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_player_player_not_found(self, client: AsyncClient):
        """Test registration with non-existent player."""
        # Create tournament dependencies
        player_response = await client.post("/players/", json={"name": "TO Player"})

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Player Not Found Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Vintage for Registration Player Not Found Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Vintage legal cards"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Player Not Found Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Try to register non-existent player
        fake_player_id = str(uuid4())
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": fake_player_id}
        )
        assert response.status_code == 404
        assert "player" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_player_max_players_reached(self, client: AsyncClient):
        """Test registration when max players is reached."""
        # Create dependencies
        to_response = await client.post("/players/", json={"name": "TO for Max Test"})

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Max Players Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Commander for Registration Max Players Test",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Commander legal cards"
        })

        # Create tournament with max_players = 1
        tournament_response = await client.post("/tournaments/", json={
            "name": "Max Players Test Tournament",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": to_response.json()["id"],
            "max_players": 1
        })
        tournament_id = tournament_response.json()["id"]

        # Register first player (should succeed)
        player1_response = await client.post("/players/", json={"name": "Max Test Player 1"})
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player1_response.json()["id"]}
        )
        assert response.status_code == 201

        # Try to register second player (should fail - max reached)
        player2_response = await client.post("/players/", json={"name": "Max Test Player 2"})
        response = await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player2_response.json()["id"]}
        )
        assert response.status_code == 400
        assert "max" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_list_registrations(self, client: AsyncClient):
        """Test listing all registrations for a tournament."""
        # Create dependencies
        to_response = await client.post("/players/", json={"name": "TO for List Test"})

        venue_response = await client.post("/venues/", json={
            "name": "LGS for List Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Limited for Registration List Test",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "card_pool": "Latest set"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "List Registrations Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": to_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Register multiple players
        player_ids = []
        for i in range(3):
            player_response = await client.post("/players/", json={"name": f"List Test Player {i}"})
            player_id = player_response.json()["id"]
            player_ids.append(player_id)

            await client.post(
                f"/tournaments/{tournament_id}/register",
                json={"player_id": player_id}
            )

        # List all registrations
        response = await client.get(f"/tournaments/{tournament_id}/registrations")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3
        assert all(reg["tournament_id"] == tournament_id for reg in data)
        assert all(reg["status"] == "active" for reg in data)

    @pytest.mark.asyncio
    async def test_list_registrations_empty(self, client: AsyncClient):
        """Test listing registrations for tournament with no players."""
        # Create tournament without registrations
        to_response = await client.post("/players/", json={"name": "TO for Empty List"})

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Empty List Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Draft for Registration Empty List Test",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "card_pool": "Draft packs"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Empty Registrations Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": to_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # List registrations (should be empty)
        response = await client.get(f"/tournaments/{tournament_id}/registrations")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_registrations_tournament_not_found(self, client: AsyncClient):
        """Test listing registrations for non-existent tournament."""
        fake_tournament_id = str(uuid4())
        response = await client.get(f"/tournaments/{fake_tournament_id}/registrations")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_drop_player(self, client: AsyncClient):
        """Test dropping a player from tournament."""
        # Create dependencies and register player
        player_response = await client.post("/players/", json={"name": "Frank"})
        player_id = player_response.json()["id"]

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Drop Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Sealed for Registration Drop Test",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "card_pool": "Sealed packs"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Drop Player Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": player_id
        })
        tournament_id = tournament_response.json()["id"]

        # Register player
        await client.post(
            f"/tournaments/{tournament_id}/register",
            json={"player_id": player_id}
        )

        # Drop player
        response = await client.delete(
            f"/tournaments/{tournament_id}/registrations/{player_id}"
        )
        assert response.status_code == 204

        # Verify player is dropped
        registrations = await client.get(f"/tournaments/{tournament_id}/registrations")
        data = registrations.json()
        dropped_reg = next((r for r in data if r["player_id"] == player_id), None)
        assert dropped_reg is not None
        assert dropped_reg["status"] == "dropped"
        assert dropped_reg["drop_time"] is not None

    @pytest.mark.asyncio
    async def test_drop_player_not_registered(self, client: AsyncClient):
        """Test dropping player who is not registered."""
        # Create tournament
        to_response = await client.post("/players/", json={"name": "TO for Drop Not Registered"})

        venue_response = await client.post("/venues/", json={
            "name": "LGS for Drop Not Registered Test"
        })

        format_response = await client.post("/formats/", json={
            "name": "Pioneer for Registration Drop Not Registered",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "card_pool": "Pioneer legal cards"
        })

        tournament_response = await client.post("/tournaments/", json={
            "name": "Drop Not Registered Test",
            "format_id": format_response.json()["id"],
            "venue_id": venue_response.json()["id"],
            "created_by": to_response.json()["id"]
        })
        tournament_id = tournament_response.json()["id"]

        # Try to drop player who was never registered
        unregistered_player = await client.post("/players/", json={"name": "Unregistered"})
        response = await client.delete(
            f"/tournaments/{tournament_id}/registrations/{unregistered_player.json()['id']}"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_drop_player_tournament_not_found(self, client: AsyncClient):
        """Test dropping player from non-existent tournament."""
        player_response = await client.post("/players/", json={"name": "Grace"})
        player_id = player_response.json()["id"]

        fake_tournament_id = str(uuid4())
        response = await client.delete(
            f"/tournaments/{fake_tournament_id}/registrations/{player_id}"
        )
        assert response.status_code == 404
