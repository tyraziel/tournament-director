#!/usr/bin/env python3
"""Test script for data layer with Mock backend.

AIA PAI Hin R Claude Code v1.0
"""

import asyncio
from src.data.mock import MockDataLayer
from src.seed import generate_kitchen_table_pauper, generate_all_seed_data


async def test_mock_backend():
    """Test Mock backend with seed data."""
    print("🧪 Testing Mock Backend Data Layer")
    print("=" * 50)
    
    # Create mock data layer
    data_layer = MockDataLayer()
    
    # Test health check
    health = await data_layer.health_check()
    print(f"Health Check: {health['status']}")
    print(f"Backend Type: {health['backend_type']}")
    
    # Test seeding with kitchen table scenario
    print(f"\n🌱 Seeding Kitchen Table Pauper scenario...")
    gen = generate_kitchen_table_pauper()
    seed_data = gen.to_dict()
    
    await data_layer.seed_data(seed_data)
    
    # Verify data was loaded
    health_after = await data_layer.health_check()
    print("Data loaded:")
    for entity_type, count in health_after['entities'].items():
        if count > 0:
            print(f"  {entity_type}: {count}")
    
    # Test some queries
    print(f"\n🔍 Testing Data Layer Queries...")
    
    # Get all players
    players = await data_layer.players.list_all()
    print(f"Players: {len(players)}")
    for player in players[:3]:  # Show first 3
        print(f"  - {player.name} (#{player.id})")
    
    # Get tournaments by status
    tournaments = await data_layer.tournaments.list_by_status("in_progress")
    print(f"In-progress tournaments: {len(tournaments)}")
    for tournament in tournaments:
        print(f"  - {tournament.name}")
    
    # Get registrations for first tournament
    if tournaments:
        tournament = tournaments[0]
        registrations = await data_layer.registrations.list_by_tournament(tournament.id)
        print(f"Registrations for '{tournament.name}': {len(registrations)}")
        for reg in registrations[:5]:  # Show first 5
            player = await data_layer.players.get_by_id(reg.player_id)
            print(f"  - Player #{reg.sequence_id}: {player.name} ({reg.status})")
    
    # Test foreign key validation
    print(f"\n🔒 Testing Foreign Key Validation...")
    try:
        # Try to create tournament with invalid format_id
        from uuid import uuid4
        from src.models.tournament import Tournament, RegistrationControl
        
        invalid_tournament = Tournament(
            id=uuid4(),
            name="Invalid Tournament",
            registration=RegistrationControl(),
            format_id=uuid4(),  # Non-existent format
            venue_id=list(data_layer._venue_repo._venues.keys())[0],  # Valid venue
            created_by=list(data_layer._player_repo._players.keys())[0]  # Valid player
        )
        
        await data_layer.tournaments.create(invalid_tournament)
        print("  ❌ Foreign key validation failed - should have thrown error")
        
    except Exception as e:
        print(f"  ✅ Foreign key validation working: {type(e).__name__}")
    
    # Test duplicate prevention
    print(f"\n🚫 Testing Duplicate Prevention...")
    try:
        # Try to create player with duplicate name
        first_player = players[0]
        duplicate_player = Player(
            id=uuid4(),
            name=first_player.name  # Duplicate name
        )
        
        await data_layer.players.create(duplicate_player)
        print("  ❌ Duplicate prevention failed - should have thrown error")
        
    except Exception as e:
        print(f"  ✅ Duplicate prevention working: {type(e).__name__}")
    
    # Test sequence ID assignment
    print(f"\n🔢 Testing Sequence ID Assignment...")
    if tournaments:
        tournament = tournaments[0]
        next_seq_id = await data_layer.registrations.get_next_sequence_id(tournament.id)
        print(f"  Next sequence ID for '{tournament.name}': {next_seq_id}")
        
        # Should be max existing + 1
        existing_regs = await data_layer.registrations.list_by_tournament(tournament.id)
        max_existing = max(reg.sequence_id for reg in existing_regs) if existing_regs else 0
        expected = max_existing + 1
        
        if next_seq_id == expected:
            print(f"  ✅ Sequence ID calculation correct: {next_seq_id} == {expected}")
        else:
            print(f"  ❌ Sequence ID calculation wrong: {next_seq_id} != {expected}")
    
    print(f"\n" + "=" * 50)
    print("🎉 Mock Backend Test Complete!")


async def test_comprehensive_seed_data():
    """Test with comprehensive seed data."""
    print(f"\n🌍 Testing Comprehensive Seed Data...")
    print("=" * 50)
    
    data_layer = MockDataLayer()
    
    # Generate individual scenarios to avoid duplicates
    from src.seed import generate_multi_tcg_formats
    gen = generate_multi_tcg_formats()  # This one has unique players
    seed_data = gen.to_dict()
    
    await data_layer.seed_data(seed_data)
    
    # Report what was loaded
    health = await data_layer.health_check()
    print("Comprehensive seed data loaded:")
    for entity_type, count in health['entities'].items():
        if count > 0:
            print(f"  {entity_type}: {count}")
    
    # Test format queries
    mtg_formats = await data_layer.formats.list_by_game_system("magic_the_gathering")
    pokemon_formats = await data_layer.formats.list_by_game_system("pokemon")
    
    print(f"\nFormat breakdown:")
    print(f"  MTG formats: {len(mtg_formats)}")
    print(f"  Pokemon formats: {len(pokemon_formats)}")
    
    # Test tournament status distribution
    all_tournaments = await data_layer.tournaments.list_all()
    status_counts = {}
    for tournament in all_tournaments:
        status_counts[tournament.status] = status_counts.get(tournament.status, 0) + 1
    
    print(f"\nTournament status distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    print("✅ Comprehensive test complete!")


async def main():
    """Run all tests."""
    await test_mock_backend()
    await test_comprehensive_seed_data()


if __name__ == "__main__":
    asyncio.run(main())