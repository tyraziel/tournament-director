#!/usr/bin/env python3
"""Test script for seed data generation.

AIA PAI Hin R Claude Code v1.0
"""

import json
from src.seed import (
    generate_kitchen_table_pauper,
    generate_discord_swiss, 
    generate_lgs_draft,
    generate_multi_tcg_formats,
    generate_complete_tournament,
)


def test_seed_generation():
    """Test all seed data generators."""
    print("🌱 Testing Tournament Director Seed Data Generation")
    print("=" * 60)
    
    scenarios = [
        ("Kitchen Table Pauper", generate_kitchen_table_pauper),
        ("Discord Swiss", generate_discord_swiss),
        ("LGS Draft", generate_lgs_draft), 
        ("Multi-TCG Formats", generate_multi_tcg_formats),
        ("Complete Tournament", generate_complete_tournament),
    ]
    
    for name, generator in scenarios:
        print(f"\n🎯 {name}")
        print("-" * 30)
        
        try:
            gen = generator()
            data = gen.to_dict()
            
            # Count objects
            counts = {k: len(v) for k, v in data.items() if v}
            
            for obj_type, count in counts.items():
                if count > 0:
                    print(f"  {obj_type}: {count}")
                    
            # Validate some basic data integrity
            if data.get("tournaments"):
                tournament = data["tournaments"][0]
                print(f"  Tournament: '{tournament['name']}'")
                print(f"  Status: {tournament['status']}")
                
            if data.get("players"):
                player_count = len(data["players"])
                reg_count = len(data.get("registrations", []))
                print(f"  Players: {player_count}, Registrations: {reg_count}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
            
        print("  ✅ Generated successfully")
    
    print("\n" + "=" * 60)
    print("🎉 Seed data generation test complete!")


if __name__ == "__main__":
    test_seed_generation()