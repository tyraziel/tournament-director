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
