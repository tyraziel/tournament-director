"""Test fixtures for Tournament Director data models.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

# Test data constants
GAME_SYSTEMS = ["magic_the_gathering", "pokemon", "star_wars_unlimited", "nfl_five", "custom_tcg"]
BASE_FORMATS = ["constructed", "pre_constructed", "limited", "special"]
TOURNAMENT_STATUSES = [
    "draft",
    "registration_open",
    "registration_closed",
    "in_progress",
    "completed",
    "cancelled",
]
PLAYER_STATUSES = ["active", "dropped", "late_entry"]
COMPONENT_TYPES = ["swiss", "single_elimination", "round_robin", "pool_play"]


@pytest.fixture
def format_test_cases():
    """Test cases for all format examples from our design session."""
    return [
        # MTG Constructed formats (PAUPER PRIORITY!)
        {
            "name": "Pauper",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "sub_format": "Pauper",
            "card_pool": "Pauper",
        },
        {
            "name": "Standard",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "sub_format": "Standard",
            "card_pool": "Standard",
        },
        {
            "name": "Historic Pauper",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "sub_format": "Pauper",
            "card_pool": "Historic",
        },
        {
            "name": "Standard BO1",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "sub_format": "Standard",
            "card_pool": "Standard",
            "match_structure": "BO1",
        },
        {
            "name": "Modern",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "sub_format": "Modern",
            "card_pool": "Modern",
        },
        {
            "name": "Pioneer",
            "game_system": "magic_the_gathering",
            "base_format": "constructed",
            "sub_format": "Pioneer",
            "card_pool": "Pioneer",
        },
        # MTG Limited formats
        {
            "name": "Draft FIN",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "sub_format": "Traditional Draft",
            "card_pool": "FIN",
        },
        {
            "name": "Sealed FIN",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "sub_format": "Sealed",
            "card_pool": "FIN",
        },
        {
            "name": "Winston Draft",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "sub_format": "Winston Draft",
            "card_pool": "Custom Packs",
        },
        {
            "name": "Solomon Draft",
            "game_system": "magic_the_gathering",
            "base_format": "limited",
            "sub_format": "Solomon Draft",
            "card_pool": "Custom Packs",
        },
        # MTG Pre-constructed
        {
            "name": "Challenger Decks 2025",
            "game_system": "magic_the_gathering",
            "base_format": "pre_constructed",
            "sub_format": None,
            "card_pool": "Challenger Decks 2025",
        },
        # MTG Special formats
        {
            "name": "JumpStart J22",
            "game_system": "magic_the_gathering",
            "base_format": "special",
            "sub_format": "JumpStart",
            "card_pool": "J22",
        },
        {
            "name": "JumpStart J20",
            "game_system": "magic_the_gathering",
            "base_format": "special",
            "sub_format": "JumpStart",
            "card_pool": "J20",
        },
        {
            "name": "Cube Draft",
            "game_system": "magic_the_gathering",
            "base_format": "special",
            "sub_format": "Cube Draft",
            "card_pool": "Custom Cube",
        },
        # Other TCGs
        {
            "name": "Pokemon Standard",
            "game_system": "pokemon",
            "base_format": "constructed",
            "sub_format": "Standard",
            "card_pool": "Standard",
        },
        {
            "name": "Pokemon Draft",
            "game_system": "pokemon",
            "base_format": "limited",
            "sub_format": "Draft",
            "card_pool": "Current",
        },
        {
            "name": "Star Wars Standard",
            "game_system": "star_wars_unlimited",
            "base_format": "constructed",
            "sub_format": "Standard",
            "card_pool": "Standard",
        },
        {
            "name": "NFL Five Draft",
            "game_system": "nfl_five",
            "base_format": "limited",
            "sub_format": "Draft",
            "card_pool": "Current",
        },
        {
            "name": "Custom TCG Standard",
            "game_system": "custom_tcg",
            "base_format": "constructed",
            "sub_format": "Standard",
            "card_pool": "Standard",
        },
    ]


@pytest.fixture
def venue_test_cases():
    """Test cases for venue examples from our design session."""
    return [
        {"name": "Kitchen Table", "address": None, "description": "Home casual play"},
        {
            "name": "Snack House",
            "address": "That friend's place with good snacks",
            "description": "The legendary snack house",
        },
        {"name": "Basement", "address": None, "description": "Underground tournament vibes"},
        {
            "name": "Local Game Store",
            "address": "123 Main St, Anytown USA",
            "description": "Friday Night Magic venue",
        },
        {
            "name": "Discord Server",
            "address": None,
            "description": "Online tournament coordination",
        },
        {
            "name": "Convention Center",
            "address": "456 Convention Blvd",
            "description": "Large tournament events",
        },
    ]


@pytest.fixture
def player_test_cases():
    """Test cases for player data."""
    return [
        {"name": "Andrew", "discord_id": "andrew#1234", "email": "andrew@example.com"},
        {"name": "Bob", "discord_id": "bob#5678", "email": None},
        {"name": "Charlie", "discord_id": None, "email": "charlie@example.com"},
        {"name": "Dana", "discord_id": None, "email": None},
    ]


@pytest.fixture
def registration_control_test_cases():
    """Test cases for registration control scenarios."""
    now = datetime.now(timezone.utc)
    return [
        # Open tournament, no passwords
        {
            "auto_open_time": None,
            "auto_close_time": None,
            "registration_password": None,
            "late_registration_password": None,
            "to_override_password": None,
            "allow_to_override": True,
            "max_players": None,
        },
        # Password-protected tournament
        {
            "auto_open_time": None,
            "auto_close_time": None,
            "registration_password": "standard123",
            "late_registration_password": "late456",
            "to_override_password": "admin789",
            "allow_to_override": True,
            "max_players": 32,
        },
        # Time-controlled tournament
        {
            "auto_open_time": now,
            "auto_close_time": now.replace(hour=23, minute=59),
            "registration_password": None,
            "late_registration_password": None,
            "to_override_password": "emergency",
            "allow_to_override": True,
            "max_players": 16,
        },
    ]


@pytest.fixture
def tournament_test_cases():
    """Test cases for tournament scenarios."""
    return [
        # Kitchen Table Pauper
        {
            "name": "Kitchen Table Pauper Championship",
            "status": "registration_open",
            "visibility": "public",
            "description": "Monthly Pauper tournament at the kitchen table",
        },
        # Discord Swiss
        {
            "name": "Monthly Discord Standard Swiss",
            "status": "in_progress",
            "visibility": "public",
            "description": "Month-long Swiss tournament on Discord",
        },
        # Private tournament
        {
            "name": "Secret Championship",
            "status": "draft",
            "visibility": "private",
            "description": "Invitation only tournament",
        },
    ]


@pytest.fixture
def match_result_test_cases():
    """Test cases for match results including edge cases."""
    return [
        # Standard results
        {"player1_wins": 2, "player2_wins": 0, "draws": 0, "description": "2-0 win"},
        {"player1_wins": 2, "player2_wins": 1, "draws": 0, "description": "2-1 win"},
        {"player1_wins": 0, "player2_wins": 2, "draws": 0, "description": "0-2 loss"},
        {"player1_wins": 1, "player2_wins": 2, "draws": 0, "description": "1-2 loss"},
        # With draws
        {"player1_wins": 1, "player2_wins": 0, "draws": 2, "description": "1-0-2 time draw"},
        {"player1_wins": 0, "player2_wins": 1, "draws": 2, "description": "0-1-2 time draw"},
        {"player1_wins": 0, "player2_wins": 0, "draws": 3, "description": "0-0-3 all draws"},
        # BO1 results
        {"player1_wins": 1, "player2_wins": 0, "draws": 0, "description": "BO1 win"},
        {"player1_wins": 0, "player2_wins": 1, "draws": 0, "description": "BO1 loss"},
        # Concession (recorded as 2-0)
        {"player1_wins": 2, "player2_wins": 0, "draws": 0, "description": "Concession as 2-0"},
        # Bye (no opponent)
        {"player1_wins": 2, "player2_wins": 0, "draws": 0, "description": "Bye win (no opponent)"},
    ]


# Utility functions for test data generation
def generate_uuid():
    """Generate a new UUID for test data."""
    return uuid4()


def generate_test_players(count: int = 4):
    """Generate a list of test players."""
    names = ["Andrew", "Bob", "Charlie", "Dana", "Eve", "Frank", "Grace", "Henry"]
    return [
        {
            "id": generate_uuid(),
            "name": names[i % len(names)] + f"_{i}" if i >= len(names) else names[i],
            "discord_id": f"player{i}#1234" if i % 2 == 0 else None,
            "email": f"player{i}@example.com" if i % 3 == 0 else None,
        }
        for i in range(count)
    ]


def generate_test_tournament_data():
    """Generate a complete tournament test scenario."""
    players = generate_test_players(8)
    tournament_id = generate_uuid()

    return {
        "tournament": {
            "id": tournament_id,
            "name": "Test Tournament",
            "status": "in_progress",
            "visibility": "public",
        },
        "players": players,
        "registrations": [
            {
                "id": generate_uuid(),
                "tournament_id": tournament_id,
                "player_id": player["id"],
                "sequence_id": i + 1,
                "status": "active",
                "registration_time": datetime.now(timezone.utc),
            }
            for i, player in enumerate(players)
        ],
    }
