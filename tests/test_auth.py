"""
Tests for authentication models and token management.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from src.data.exceptions import DuplicateError, NotFoundError
from src.data.mock import MockDataLayer
from src.models.auth import APIKey
from src.models.player import Player
from src.utils.token import generate_api_token


class TestAPIKey:
    """Test cases for APIKey model."""

    def test_api_key_creation_valid(self):
        """Test creating a valid API key."""
        player_id = uuid4()
        token = "a" * 64  # 64-char token

        api_key = APIKey(
            token=token,
            name="Test API Key",
            created_by=player_id,
        )

        assert api_key.id is not None
        assert api_key.token == token
        assert api_key.name == "Test API Key"
        assert api_key.created_by == player_id
        assert api_key.is_active is True
        assert api_key.expires_at is None
        assert api_key.last_used_at is None
        assert api_key.permissions is None

    def test_api_key_with_expiration(self):
        """Test creating an API key with expiration date."""
        player_id = uuid4()
        expires = datetime.utcnow() + timedelta(days=30)

        api_key = APIKey(
            token="b" * 64,
            name="Expiring Key",
            created_by=player_id,
            expires_at=expires,
        )

        assert api_key.expires_at == expires

    def test_api_key_with_permissions(self):
        """Test creating an API key with permissions."""
        player_id = uuid4()
        permissions = {"read": True, "write": False, "admin": False}

        api_key = APIKey(
            token="c" * 64,
            name="Limited Key",
            created_by=player_id,
            permissions=permissions,
        )

        assert api_key.permissions == permissions

    def test_api_key_validation_token_too_short(self):
        """Test that token must be at least 32 characters."""
        player_id = uuid4()

        with pytest.raises(ValueError):
            APIKey(
                token="tooshort",  # Less than 32 chars
                name="Invalid Key",
                created_by=player_id,
            )

    def test_api_key_validation_token_too_long(self):
        """Test that token cannot exceed 256 characters."""
        player_id = uuid4()

        with pytest.raises(ValueError):
            APIKey(
                token="x" * 300,  # More than 256 chars
                name="Invalid Key",
                created_by=player_id,
            )

    def test_api_key_validation_name_empty(self):
        """Test that name cannot be empty."""
        player_id = uuid4()

        with pytest.raises(ValueError):
            APIKey(
                token="d" * 64,
                name="",  # Empty name
                created_by=player_id,
            )

    def test_api_key_can_be_deactivated(self):
        """Test that API key can be deactivated."""
        player_id = uuid4()

        api_key = APIKey(
            token="e" * 64,
            name="Test Key",
            created_by=player_id,
        )

        assert api_key.is_active is True

        # Deactivate
        api_key.is_active = False

        assert api_key.is_active is False

    def test_api_key_last_used_tracking(self):
        """Test that last_used_at can be updated."""
        player_id = uuid4()

        api_key = APIKey(
            token="f" * 64,
            name="Test Key",
            created_by=player_id,
        )

        assert api_key.last_used_at is None

        # Update last used
        now = datetime.utcnow()
        api_key.last_used_at = now

        assert api_key.last_used_at == now


class TestTokenGeneration:
    """Test cases for token generation utility."""

    def test_generate_api_token_default_length(self):
        """Test generating token with default length."""
        token = generate_api_token()

        assert len(token) == 128  # 64 bytes * 2 (hex)
        assert isinstance(token, str)
        # Verify it's hex
        int(token, 16)  # Should not raise

    def test_generate_api_token_custom_length(self):
        """Test generating token with custom length."""
        token = generate_api_token(32)

        assert len(token) == 64  # 32 bytes * 2 (hex)

    def test_generate_api_token_unique(self):
        """Test that generated tokens are unique."""
        tokens = [generate_api_token() for _ in range(100)]

        # All tokens should be unique
        assert len(set(tokens)) == 100


class TestAPIKeyRepository:
    """Test cases for APIKey repository operations."""

    @pytest.mark.asyncio
    async def test_create_api_key(self):
        """Test creating an API key."""
        data_layer = MockDataLayer()
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(
            token=token,
            name="Test API Key",
            created_by=player.id,
        )

        created = await data_layer.api_keys.create(api_key)

        assert created.id == api_key.id
        assert created.token == token
        assert created.name == "Test API Key"
        assert created.created_by == player.id

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        """Test retrieving API key by ID."""
        data_layer = MockDataLayer()
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        retrieved = await data_layer.api_keys.get_by_id(api_key.id)

        assert retrieved.id == api_key.id
        assert retrieved.token == token

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test that NotFoundError is raised for non-existent ID."""
        data_layer = MockDataLayer()

        with pytest.raises(NotFoundError):
            await data_layer.api_keys.get_by_id(uuid4())

    @pytest.mark.asyncio
    async def test_get_by_token(self):
        """Test retrieving API key by token."""
        data_layer = MockDataLayer()
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        retrieved = await data_layer.api_keys.get_by_token(token)

        assert retrieved is not None
        assert retrieved.id == api_key.id
        assert retrieved.token == token

    @pytest.mark.asyncio
    async def test_get_by_token_not_found(self):
        """Test that None is returned for non-existent token."""
        data_layer = MockDataLayer()

        retrieved = await data_layer.api_keys.get_by_token("nonexistent")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_by_owner(self):
        """Test listing API keys by owner."""
        data_layer = MockDataLayer()
        player1 = Player(id=uuid4(), name="Player 1")
        player2 = Player(id=uuid4(), name="Player 2")
        await data_layer.players.create(player1)
        await data_layer.players.create(player2)

        # Create keys for player 1
        key1 = APIKey(token=generate_api_token(), name="Key 1", created_by=player1.id)
        key2 = APIKey(token=generate_api_token(), name="Key 2", created_by=player1.id)

        # Create key for player 2
        key3 = APIKey(token=generate_api_token(), name="Key 3", created_by=player2.id)

        await data_layer.api_keys.create(key1)
        await data_layer.api_keys.create(key2)
        await data_layer.api_keys.create(key3)

        # Get player 1's keys
        player1_keys = await data_layer.api_keys.list_by_owner(player1.id)

        assert len(player1_keys) == 2
        assert all(k.created_by == player1.id for k in player1_keys)
        # Should be ordered by created_at descending (newest first)
        assert player1_keys[0].created_at >= player1_keys[1].created_at

    @pytest.mark.asyncio
    async def test_update_api_key(self):
        """Test updating an API key."""
        data_layer = MockDataLayer()
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        # Update the key (deactivate it)
        api_key.is_active = False
        api_key.last_used_at = datetime.utcnow()

        updated = await data_layer.api_keys.update(api_key)

        assert updated.is_active is False
        assert updated.last_used_at is not None

    @pytest.mark.asyncio
    async def test_delete_api_key(self):
        """Test deleting an API key."""
        data_layer = MockDataLayer()
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        await data_layer.api_keys.delete(api_key.id)

        # Should raise NotFoundError now
        with pytest.raises(NotFoundError):
            await data_layer.api_keys.get_by_id(api_key.id)

        # Token lookup should also fail
        assert await data_layer.api_keys.get_by_token(token) is None

    @pytest.mark.asyncio
    async def test_duplicate_token_rejected(self):
        """Test that duplicate tokens are rejected."""
        data_layer = MockDataLayer()
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key1 = APIKey(token=token, name="Key 1", created_by=player.id)
        await data_layer.api_keys.create(api_key1)

        # Try to create another key with same token
        api_key2 = APIKey(token=token, name="Key 2", created_by=player.id)

        with pytest.raises(DuplicateError):
            await data_layer.api_keys.create(api_key2)


class TestLocalAPIKeyRepository:
    """Test cases for LocalAPIKeyRepository with file persistence.

    AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
    """

    @pytest.mark.asyncio
    async def test_local_api_key_persistence(self, tmp_path):
        """Test that API keys persist to file system."""
        from src.data.local import LocalDataLayer

        data_layer = LocalDataLayer(str(tmp_path))

        # Create a player and API key
        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        created = await data_layer.api_keys.create(api_key)

        assert created.id == api_key.id
        assert created.token == token

        # Verify file was created
        api_keys_file = tmp_path / "api_keys.json"
        assert api_keys_file.exists()

        # Create new data layer instance to verify persistence
        data_layer2 = LocalDataLayer(str(tmp_path))
        retrieved = await data_layer2.api_keys.get_by_token(token)

        assert retrieved is not None
        assert retrieved.id == api_key.id
        assert retrieved.token == token
        assert retrieved.name == "Test Key"

    @pytest.mark.asyncio
    async def test_local_get_by_token_after_reload(self, tmp_path):
        """Test get_by_token works after reloading from file."""
        from src.data.local import LocalDataLayer

        data_layer = LocalDataLayer(str(tmp_path))

        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        # Create new instance and verify token lookup
        data_layer2 = LocalDataLayer(str(tmp_path))
        retrieved = await data_layer2.api_keys.get_by_token(token)

        assert retrieved is not None
        assert retrieved.id == api_key.id
        assert retrieved.token == token

    @pytest.mark.asyncio
    async def test_local_list_by_owner_after_reload(self, tmp_path):
        """Test list_by_owner works after reloading from file."""
        from src.data.local import LocalDataLayer

        data_layer = LocalDataLayer(str(tmp_path))

        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        # Create multiple API keys
        key1 = APIKey(token=generate_api_token(), name="Key 1", created_by=player.id)
        key2 = APIKey(token=generate_api_token(), name="Key 2", created_by=player.id)
        await data_layer.api_keys.create(key1)
        await data_layer.api_keys.create(key2)

        # Reload and verify list_by_owner
        data_layer2 = LocalDataLayer(str(tmp_path))
        keys = await data_layer2.api_keys.list_by_owner(player.id)

        assert len(keys) == 2
        assert all(k.created_by == player.id for k in keys)

    @pytest.mark.asyncio
    async def test_local_duplicate_token_prevention(self, tmp_path):
        """Test that duplicate tokens are prevented in local backend."""
        from src.data.local import LocalDataLayer

        data_layer = LocalDataLayer(str(tmp_path))

        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key1 = APIKey(token=token, name="Key 1", created_by=player.id)
        await data_layer.api_keys.create(api_key1)

        # Try to create duplicate
        api_key2 = APIKey(token=token, name="Key 2", created_by=player.id)

        with pytest.raises(DuplicateError):
            await data_layer.api_keys.create(api_key2)

    @pytest.mark.asyncio
    async def test_local_update_api_key(self, tmp_path):
        """Test updating API key persists to file."""
        from src.data.local import LocalDataLayer

        data_layer = LocalDataLayer(str(tmp_path))

        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        # Update the key
        api_key.is_active = False
        api_key.last_used_at = datetime.utcnow()
        await data_layer.api_keys.update(api_key)

        # Reload and verify update persisted
        data_layer2 = LocalDataLayer(str(tmp_path))
        retrieved = await data_layer2.api_keys.get_by_id(api_key.id)

        assert retrieved.is_active is False
        assert retrieved.last_used_at is not None

    @pytest.mark.asyncio
    async def test_local_delete_api_key(self, tmp_path):
        """Test deleting API key persists to file."""
        from src.data.local import LocalDataLayer

        data_layer = LocalDataLayer(str(tmp_path))

        player = Player(id=uuid4(), name="Test Player")
        await data_layer.players.create(player)

        token = generate_api_token()
        api_key = APIKey(token=token, name="Test Key", created_by=player.id)
        await data_layer.api_keys.create(api_key)

        # Delete the key
        await data_layer.api_keys.delete(api_key.id)

        # Reload and verify deletion persisted
        data_layer2 = LocalDataLayer(str(tmp_path))

        with pytest.raises(NotFoundError):
            await data_layer2.api_keys.get_by_id(api_key.id)

        assert await data_layer2.api_keys.get_by_token(token) is None
