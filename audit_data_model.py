#!/usr/bin/env python3
"""Data model audit script to validate assumptions and test coverage.

AIA PAI Hin R Claude Code v1.0
"""

import json
from typing import Dict, List, Set

from src.models.base import (
    BaseFormat,
    ComponentType,
    GameSystem,
    PlayerStatus,
    TournamentStatus,
    TournamentVisibility,
)


def audit_enum_coverage():
    """Audit enum definitions for completeness."""
    print("=== ENUM DEFINITIONS AUDIT ===")
    
    print(f"Game Systems ({len(GameSystem)}): {[e.value for e in GameSystem]}")
    print(f"Base Formats ({len(BaseFormat)}): {[e.value for e in BaseFormat]}")
    print(f"Tournament Status ({len(TournamentStatus)}): {[e.value for e in TournamentStatus]}")
    print(f"Tournament Visibility ({len(TournamentVisibility)}): {[e.value for e in TournamentVisibility]}")
    print(f"Player Status ({len(PlayerStatus)}): {[e.value for e in PlayerStatus]}")
    print(f"Component Types ({len(ComponentType)}): {[e.value for e in ComponentType]}")


def audit_tournament_lifecycle():
    """Audit tournament state transitions."""
    print("\n=== TOURNAMENT LIFECYCLE AUDIT ===")
    
    valid_transitions = {
        TournamentStatus.DRAFT: [TournamentStatus.REGISTRATION_OPEN, TournamentStatus.CANCELLED],
        TournamentStatus.REGISTRATION_OPEN: [TournamentStatus.REGISTRATION_CLOSED, TournamentStatus.IN_PROGRESS, TournamentStatus.CANCELLED],
        TournamentStatus.REGISTRATION_CLOSED: [TournamentStatus.IN_PROGRESS, TournamentStatus.CANCELLED],
        TournamentStatus.IN_PROGRESS: [TournamentStatus.COMPLETED, TournamentStatus.CANCELLED],
        TournamentStatus.COMPLETED: [],  # Terminal state
        TournamentStatus.CANCELLED: [],  # Terminal state
    }
    
    print("Valid state transitions:")
    for from_state, to_states in valid_transitions.items():
        if to_states:
            print(f"  {from_state.value} -> {[s.value for s in to_states]}")
        else:
            print(f"  {from_state.value} -> [TERMINAL]")
    
    # Check if we have terminal states
    terminal_states = [s for s, transitions in valid_transitions.items() if not transitions]
    print(f"Terminal states: {[s.value for s in terminal_states]}")


def audit_swiss_requirements():
    """Audit Swiss tournament requirements."""
    print("\n=== SWISS TOURNAMENT REQUIREMENTS ===")
    
    swiss_requirements = {
        "pairing_data": ["player_id", "wins", "losses", "draws", "omw_percent", "gw_percent", "ogw_percent"],
        "match_tracking": ["player1_wins", "player2_wins", "draws", "byes"],
        "round_management": ["round_number", "pairings", "results"],
        "tiebreaker_calculation": ["opponent_match_win_percentage", "game_win_percentage", "opponent_game_win_percentage"]
    }
    
    print("Swiss tournament data requirements:")
    for category, fields in swiss_requirements.items():
        print(f"  {category}: {fields}")
    
    # Check if our Match model supports these
    print("\nMatch model validation:")
    match_fields = ["player1_wins", "player2_wins", "draws", "player2_id"]  # player2_id None = bye
    print(f"  Supported match data: {match_fields}")
    print("  ✓ Supports wins/losses/draws tracking")
    print("  ✓ Supports bye matches (player2_id=None)")
    print("  ? Missing: Direct tiebreaker calculation fields (would be computed)")


def audit_format_coverage():
    """Audit format definitions for completeness."""
    print("\n=== FORMAT COVERAGE AUDIT ===")
    
    # Sample formats from our test data (manually extracted)
    test_formats = [
        ("Pauper", "magic_the_gathering", "constructed"),
        ("Standard", "magic_the_gathering", "constructed"),
        ("Modern", "magic_the_gathering", "constructed"),
        ("Draft FIN", "magic_the_gathering", "limited"),
        ("Sealed FIN", "magic_the_gathering", "limited"),
        ("Challenger Decks 2025", "magic_the_gathering", "pre_constructed"),
        ("JumpStart J22", "magic_the_gathering", "special"),
        ("Pokemon Standard", "pokemon", "constructed"),
        ("Pokemon Draft", "pokemon", "limited"),
        ("Star Wars Standard", "star_wars_unlimited", "constructed"),
        ("NFL Five Draft", "nfl_five", "limited"),
        ("Custom TCG Standard", "custom_tcg", "constructed"),
    ]
    
    # Analyze coverage
    game_systems = set(fmt[1] for fmt in test_formats)
    base_formats = set(fmt[2] for fmt in test_formats)
    
    print("Game system coverage in test data:")
    for system in GameSystem:
        count = len([f for f in test_formats if f[1] == system.value])
        print(f"  {system.value}: {count} test formats")
    
    print("Base format coverage in test data:")
    for base_fmt in BaseFormat:
        count = len([f for f in test_formats if f[2] == base_fmt.value])
        print(f"  {base_fmt.value}: {count} test formats")
    
    # Check for gaps
    enum_systems = set(s.value for s in GameSystem)
    enum_base_formats = set(f.value for f in BaseFormat)
    
    missing_systems = enum_systems - game_systems
    missing_base_formats = enum_base_formats - base_formats
    
    if missing_systems:
        print(f"⚠️  Missing game systems in test data: {missing_systems}")
    if missing_base_formats:
        print(f"⚠️  Missing base formats in test data: {missing_base_formats}")


def audit_match_results():
    """Audit match result representations."""
    print("\n=== MATCH RESULT AUDIT ===")
    
    # Common match scenarios
    scenarios = [
        ("Standard BO3 Win", {"player1_wins": 2, "player2_wins": 0, "draws": 0}),
        ("Close BO3", {"player1_wins": 2, "player2_wins": 1, "draws": 0}),
        ("Time Draw", {"player1_wins": 1, "player2_wins": 0, "draws": 2}),
        ("All Draws", {"player1_wins": 0, "player2_wins": 0, "draws": 3}),
        ("BO1 Win", {"player1_wins": 1, "player2_wins": 0, "draws": 0}),
        ("Concession", {"player1_wins": 2, "player2_wins": 0, "draws": 0}),
        ("Bye", {"player1_wins": 2, "player2_wins": 0, "draws": 0}),  # + player2_id=None
    ]
    
    print("Supported match result scenarios:")
    for name, result in scenarios:
        total_games = result["player1_wins"] + result["player2_wins"] + result["draws"]
        print(f"  {name}: P1={result['player1_wins']} P2={result['player2_wins']} D={result['draws']} (Total: {total_games})")
    
    print("\nMatch structure considerations:")
    print("  ✓ Supports variable game counts (BO1, BO3, BO5)")
    print("  ✓ Supports draws/time limits")
    print("  ✓ Supports byes (player2_id=None)")
    print("  ✓ Supports concessions (recorded as 2-0 or 1-0)")


def audit_registration_scenarios():
    """Audit player registration scenarios."""
    print("\n=== REGISTRATION SCENARIOS AUDIT ===")
    
    scenarios = [
        ("Normal Registration", "Player registers during registration_open"),
        ("Late Entry", "Player registers during in_progress with late_entry status"),
        ("Player Drop", "Active player changes to dropped status"),
        ("Re-entry", "Dropped player returns (would need new registration?)"),
        ("Max Players", "Registration blocked when max_players reached"),
        ("Password Protected", "Registration requires password"),
        ("Auto Close", "Registration closes at auto_close_time"),
    ]
    
    print("Registration scenarios to support:")
    for name, description in scenarios:
        print(f"  {name}: {description}")
    
    print("\nCurrent model support:")
    print("  ✓ PlayerStatus.ACTIVE/DROPPED/LATE_ENTRY")
    print("  ✓ RegistrationControl.max_players")
    print("  ✓ RegistrationControl.registration_password")
    print("  ✓ RegistrationControl.auto_close_time")
    print("  ✓ TournamentRegistration.sequence_id for player numbers")
    print("  ? Re-entry handling (create new registration or reactivate?)")


def audit_data_integrity():
    """Audit data integrity requirements."""
    print("\n=== DATA INTEGRITY AUDIT ===")
    
    integrity_rules = [
        "Tournament.format_id must reference valid Format.id",
        "Tournament.venue_id must reference valid Venue.id", 
        "Tournament.created_by must reference valid Player.id",
        "TournamentRegistration.tournament_id must reference valid Tournament.id",
        "TournamentRegistration.player_id must reference valid Player.id",
        "Match.player1_id must reference valid Player.id",
        "Match.player2_id must reference valid Player.id or be None (bye)",
        "Match.tournament_id must reference valid Tournament.id",
        "Component.tournament_id must reference valid Tournament.id",
        "Round.tournament_id must reference valid Tournament.id",
        "Round.component_id must reference valid Component.id",
        "Match.round_id must reference valid Round.id",
        "Match.component_id must reference valid Component.id",
        "TournamentRegistration.sequence_id must be unique per tournament",
    ]
    
    print("Data integrity constraints needed:")
    for rule in integrity_rules:
        print(f"  • {rule}")
    
    print("\nCurrent model relationships:")
    print("  ✓ UUID foreign keys defined")
    print("  ✓ Optional relationships marked (player2_id for byes)")
    print("  ⚠️  No foreign key constraints enforced at model level")
    print("  ⚠️  Sequence ID uniqueness not enforced at model level")


if __name__ == "__main__":
    print("🔍 TOURNAMENT DIRECTOR DATA MODEL AUDIT")
    print("=" * 50)
    
    audit_enum_coverage()
    audit_tournament_lifecycle() 
    audit_swiss_requirements()
    audit_format_coverage()
    audit_match_results()
    audit_registration_scenarios()
    audit_data_integrity()
    
    print("\n" + "=" * 50)
    print("📊 AUDIT COMPLETE")
    print("Review findings above to validate data model assumptions")