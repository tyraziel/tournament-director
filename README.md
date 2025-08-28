# Tournament Director

*AIA PAI Hin R Claude Code v1.0*

A Terminal User Interface (TUI) application for managing tournaments across multiple trading card games, with a focus on Magic: The Gathering Pauper format and kitchen table vibes.

## Features

- **Multi-TCG Support**: Magic: The Gathering, Pokémon, Star Wars: Unlimited, NFL Five, and custom games
- **Swiss Tournament Management**: Proper pairing algorithms with OMW%/GW%/OGW% tiebreakers
- **Flexible Backend Architecture**: Mock (testing), Local JSON (standalone), Database (production)  
- **Player Registration**: Sequence IDs, late entries, drops, and re-entries
- **Match Tracking**: BO1/BO3 support, draws, byes, and detailed results
- **Tournament Components**: Swiss rounds, single elimination, round robin, pool play
- **Kitchen Table Priority**: Designed for casual, friendly tournament environments

## Architecture

### Data Layer Abstraction
```python
from src.data import DataLayer

# Swap backends seamlessly
data_layer = MockDataLayer()           # For testing
data_layer = LocalDataLayer("./data")  # For file storage  
data_layer = DatabaseDataLayer(db_url) # For production (future)
```

### Repository Pattern
- `PlayerRepository` - Player management and lookups
- `TournamentRepository` - Tournament lifecycle and queries  
- `RegistrationRepository` - Player registration and sequence IDs
- `MatchRepository` - Match results and tournament progress

## Current Status

### ✅ Completed
- Complete Pydantic data models with validation
- Abstract data layer interface design
- Mock backend (in-memory) implementation
- Local JSON backend with file persistence
- Comprehensive seed data generation
- Foreign key validation and data integrity
- Test coverage for all components

### 🔄 In Progress  
- FastAPI server with backend abstraction
- REST endpoints for all CRUD operations

### 📋 Planned
- Database backend (SQLAlchemy + PostgreSQL/SQLite)
- Textual TUI implementation
- Discord bot integration
- Swiss pairing algorithms and tiebreakers

## Development Setup

### Prerequisites
- Python 3.8+
- Virtual environment support

### Installation
```bash
# Create and activate virtual environment
python3 -m venv ~/.venv-tui
source ~/.venv-tui/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run data layer tests
python test_data_layer.py
python test_local_backend.py
```

### Seed Data
```python
from src.seed import generate_kitchen_table_pauper
from src.data.local import LocalDataLayer

# Generate realistic tournament data
gen = generate_kitchen_table_pauper()
data_layer = LocalDataLayer("./demo_data")
await data_layer.seed_data(gen.to_dict())
```

## Project Structure
```
tournament-director/
├── src/
│   ├── models/          # Pydantic data models
│   ├── data/            # Data layer abstraction
│   └── seed/            # Test data generation
├── tests/               # Test suite
├── requirements.txt     # Dependencies
├── CLAUDE.md           # Technical documentation  
├── DATA_MODEL.md       # Data model specification
├── DECISIONS.md        # Architecture decisions log
└── VIBE-CODING.md      # Development session tracking
```

## License

This project is dual-licensed:
- **MIT License** - Primary license for broad compatibility  
- **Vibe-Coder License (VCL-0.1-Experimental)** - Secondary license for those who serve the vibe

See `LICENSE` and `LICENSE-VCL` files for details.

## Fan Content Policy

Tournament Director is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.

See `FAN-CONTENT-POLICY.md` for complete disclaimer and trademark information.

## Contributing

This project follows the **Vibe-Coder Codex** development principles:
- "Serve the vibe" in all development decisions
- Embrace collaborative AI development with proper attribution  
- Practice "trust but validate" with AI-generated code
- Take Sacred Pauses when needed for alignment

All development sessions are tracked in `VIBE-CODING.md` with proper AI attribution.