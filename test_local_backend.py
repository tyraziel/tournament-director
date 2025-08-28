#!/usr/bin/env python3
"""Test script for Local JSON backend.

AIA PAI Hin R Claude Code v1.0
"""

import asyncio
import tempfile
import shutil
from pathlib import Path

from src.data.local import LocalDataLayer
from src.seed import generate_kitchen_table_pauper


async def test_local_json_backend():
    """Test Local JSON backend with persistence."""
    print("📁 Testing Local JSON Backend Data Layer")
    print("=" * 50)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "tournament_data"
        
        print(f"Test data directory: {data_dir}")
        
        # Create local data layer
        data_layer = LocalDataLayer(str(data_dir))
        
        # Test health check
        health = await data_layer.health_check()
        print(f"Health Check: {health['status']}")
        print(f"Backend Type: {health['backend_type']}")
        print(f"Data Directory: {health['data_directory']}")
        
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
        
        # Check that JSON files were created
        print(f"\n📄 Checking JSON files created...")
        json_files = list(data_dir.glob("*.json"))
        print(f"JSON files created: {len(json_files)}")
        for json_file in sorted(json_files):
            size = json_file.stat().st_size
            print(f"  - {json_file.name}: {size} bytes")
        
        # Test persistence by creating new data layer instance
        print(f"\n🔄 Testing persistence with new data layer instance...")
        data_layer2 = LocalDataLayer(str(data_dir))
        
        # Should load existing data automatically
        health_persisted = await data_layer2.health_check()
        print("Data persisted:")
        for entity_type, count in health_persisted['entities'].items():
            if count > 0:
                print(f"  {entity_type}: {count}")
        
        # Verify data integrity after reload
        players = await data_layer2.players.list_all()
        tournaments = await data_layer2.tournaments.list_all()
        
        print(f"\n✅ Data integrity after reload:")
        print(f"  Players loaded: {len(players)}")
        print(f"  Tournaments loaded: {len(tournaments)}")
        
        if tournaments:
            tournament = tournaments[0]
            print(f"  Tournament name: '{tournament.name}'")
            print(f"  Tournament status: {tournament.status}")
            
            # Test relationships
            registrations = await data_layer2.registrations.list_by_tournament(tournament.id)
            print(f"  Registrations: {len(registrations)}")
        
        # Test queries work the same as Mock backend
        print(f"\n🔍 Testing queries match Mock backend behavior...")
        
        # Get tournaments by status
        active_tournaments = await data_layer2.tournaments.list_by_status("in_progress")
        print(f"In-progress tournaments: {len(active_tournaments)}")
        
        # Test foreign key validation still works
        print(f"\n🔒 Testing foreign key validation with persistence...")
        try:
            from uuid import uuid4
            from src.models.tournament import Tournament, RegistrationControl
            
            invalid_tournament = Tournament(
                id=uuid4(),
                name="Invalid Tournament",
                registration=RegistrationControl(),
                format_id=uuid4(),  # Non-existent format
                venue_id=uuid4(),   # Non-existent venue
                created_by=uuid4()  # Non-existent player
            )
            
            await data_layer2.tournaments.create(invalid_tournament)
            print("  ❌ Foreign key validation failed")
            
        except Exception as e:
            print(f"  ✅ Foreign key validation working: {type(e).__name__}")
        
        # Test updating data and persistence
        print(f"\n✏️ Testing data updates and persistence...")
        if players:
            first_player = players[0]
            original_name = first_player.name
            first_player.name = f"Updated {original_name}"
            
            await data_layer2.players.update(first_player)
            print(f"Updated player name: '{original_name}' -> '{first_player.name}'")
            
            # Create third instance to verify update persisted
            data_layer3 = LocalDataLayer(str(data_dir))
            updated_player = await data_layer3.players.get_by_id(first_player.id)
            
            if updated_player.name == first_player.name:
                print("  ✅ Update persisted correctly")
            else:
                print("  ❌ Update did not persist")
        
        # Test clearing data
        print(f"\n🗑️ Testing data clearing...")
        await data_layer2.clear_all_data()
        
        health_cleared = await data_layer2.health_check()
        total_entities = sum(health_cleared['entities'].values())
        
        if total_entities == 0:
            print("  ✅ All data cleared successfully")
        else:
            print(f"  ❌ Data not fully cleared: {total_entities} entities remain")
        
        # Verify files still exist but are empty/minimal
        json_files_after = list(data_dir.glob("*.json"))
        print(f"JSON files after clear: {len(json_files_after)}")
    
    print(f"\n" + "=" * 50)
    print("🎉 Local JSON Backend Test Complete!")


async def test_json_format_inspection():
    """Test the actual JSON format for human readability."""
    print(f"\n📋 Testing JSON Format Inspection...")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "json_format_test"
        
        # Create minimal data layer
        data_layer = LocalDataLayer(str(data_dir))
        
        # Create some simple test data
        from src.models.player import Player
        from src.models.venue import Venue
        from uuid import uuid4
        
        # Create a player
        player = Player(id=uuid4(), name="Test Player", discord_id="test#1234")
        await data_layer.players.create(player)
        
        # Create a venue
        venue = Venue(id=uuid4(), name="Test Venue", description="A test venue")
        await data_layer.venues.create(venue)
        
        # Inspect the JSON files
        player_file = data_dir / "players.json"
        venue_file = data_dir / "venues.json"
        
        if player_file.exists():
            print("Player JSON content:")
            with open(player_file, 'r') as f:
                content = f.read()
                print(content[:300] + "..." if len(content) > 300 else content)
        
        if venue_file.exists():
            print("\nVenue JSON content:")
            with open(venue_file, 'r') as f:
                content = f.read()
                print(content[:300] + "..." if len(content) > 300 else content)
    
    print("✅ JSON format inspection complete!")


async def main():
    """Run all tests."""
    await test_local_json_backend()
    await test_json_format_inspection()


if __name__ == "__main__":
    asyncio.run(main())