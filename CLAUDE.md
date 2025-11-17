# Tournament Director TUI

*AIA PAI Hin R Claude Code v1.0 // AIA Primarily AI, Human-initiated, Reviewed, Claude Code v1.0 // This work was primarily AI-generated. AI was prompted for its contributions, or AI assistance was enabled. AI-generated content was reviewed and approved. The following model(s) or application(s) were used: Claude Code.*

## Project Overview
A Terminal User Interface (TUI) application built with Python and Textual framework for tournament management and direction.

## AI Attribution
AIA PAI Hin R Claude Code v1.0 // AIA Primarily AI, Human-initiated, Reviewed, Claude Code v1.0 // This work was primarily AI-generated. AI was prompted for its contributions, or AI assistance was enabled. AI-generated content was reviewed and approved. The following model(s) or application(s) were used: Claude Code.

## Licensing
This project is dual-licensed under:
- **MIT License** - Primary license for legal certainty and broad compatibility
- **Vibe-Coder License (VCL-0.1-Experimental)** - Secondary license for those who serve the vibe

The VCL is a novelty license created for fun and cultural purposes with no legal bearing. The MIT license provides the legally binding terms.

## Development Team
- **Vibe Coder**: Andrew Potozniak <tyraziel@gmail.com>
- **AI Assistant**: Claude Code (Anthropic)

## Design Principles (Based on MTGA Mythic Tracker TUI)

### Architecture Philosophy
- **Modular Design**: Clear separation of concerns with dedicated modules
- **Type Safety**: Pydantic validation for all data models
- **Error Handling**: Comprehensive error handling for file I/O and parsing
- **Testing Strategy**: Each component has dedicated test files
- **Configuration Management**: JSON-based settings with validation

### TUI Framework Standards
- **Textual Framework**: Professional terminal user interface using Python Textual
- **Clean Layout**: Side-panel designs with clear information hierarchy
- **Keyboard Navigation**: Intuitive keybindings for all major actions
- **Real-time Updates**: Live data updates without screen flicker
- **Visual Indicators**: Clear status indicators and progress displays

### Code Quality Standards
- **Type Hints**: Type annotations throughout codebase
- **Documentation**: Comprehensive inline documentation
- **Import Organization**: Clean, organized imports
- **Consistent Naming**: Clear, descriptive variable and function names
- **No Unnecessary Comments**: Code should be self-documenting

### Project Structure Convention
```
project-root/
├── src/
│   ├── models/          # Data structures and business logic
│   ├── config/          # Configuration management
│   ├── core/            # Application state and management
│   ├── ui/              # TUI framework components
│   └── utils/           # Utility functions and helpers
├── tests/               # Test files (test_*.py format)
├── requirements.txt     # Python dependencies
├── main.py              # Main application entry point
├── CLAUDE.md            # Technical documentation
└── README.md            # User-facing documentation
```

### Development Practices
- **Virtual Environment**: Use dedicated venv for dependencies
- **Session Tracking**: Log development sessions in VIBE-CODING.md
- **Prompt Logging**: Track all AI interactions for context
- **Git Practices**: No automatic commits unless explicitly requested
- **Testing Focus**: Comprehensive test coverage with mock data
- **Vibe-Coder Principles**: Follow the Vibe-Coder Codex guidelines
  - "Serve the vibe" in all development decisions
  - Embrace collaborative AI development with proper attribution
  - Practice "trust but validate" with AI-generated code
  - Take Sacred Pauses when needed for alignment

### TUI Design Patterns
- **Panel-based Layout**: Multiple information panels with clear separation
- **Context Switching**: Tab navigation between different views
- **Status Bars**: Always-visible status and control information
- **Modal Dialogs**: For configuration and detailed input forms
- **Live Data**: Real-time updates for dynamic information

### Configuration Management
- **Default Paths**: Use `~/.config/app-name/` for user configuration
- **JSON Format**: Human-readable configuration files
- **Auto-detection**: Intelligent path detection where possible
- **Validation**: Pydantic models for configuration validation
- **CLI Override**: Command-line arguments override config files

### State Management
- **Persistence**: Automatic state saving for crash recovery
- **Session Management**: Track user sessions with start/stop/pause
- **Live State**: Maintain application state across restarts
- **Data Integrity**: Validation and error recovery for corrupted state

## Development Commands

### Setup
```bash
# Set up virtual environment
python3 -m venv ~/.venv-tui
source ~/.venv-tui/bin/activate
pip install -r requirements.txt
```

### Running
```bash
# Activate virtual environment first
source ~/.venv-tui/bin/activate

# Run main application
python3 main.py

# Show command line options
python3 main.py --help
```

### Testing
```bash
# Run all tests (activate venv first)
source ~/.venv-tui/bin/activate
python3 -m pytest tests/ -v

# Or run individual test files
python3 test_models.py
python3 test_config.py
```

## Git Policy
- **No Automatic Git Operations**: Never run git add, git commit, or git push unless explicitly requested by user
- **Manual Control**: All version control operations must be human-initiated
- **Branch Safety**: Never create or switch branches automatically

## Project Status
🚧 **In Development** - Setting up project foundation based on proven MTGA TUI design principles

## Technical Stack
- **Language**: Python 3.7+
- **TUI Framework**: Textual
- **Validation**: Pydantic
- **Configuration**: JSON
- **Testing**: pytest (planned)
- **Development**: Claude Code AI assistance

## Backend Architecture

The Tournament Director uses a **three-backend data layer architecture** for maximum flexibility:

### Backend Types
1. **Mock Backend** - In-memory storage for testing and development
2. **Local JSON Backend** - File-based persistence for standalone tournaments
3. **Database Backend** - PostgreSQL/SQLite for production (future implementation)

### Data Layer Interface
All backends implement the same abstract interface:
```python
from src.data import DataLayer

# Swap backends seamlessly
data_layer = MockDataLayer()           # For testing
data_layer = LocalDataLayer("./data")  # For file storage
data_layer = DatabaseDataLayer(db_url) # For production (future)

# Same API for all backends
players = await data_layer.players.list_all()
tournament = await data_layer.tournaments.get_by_id(tournament_id)
```

### Repository Pattern
Each entity has its own repository with full CRUD operations:
- `PlayerRepository` - Player management and lookups
- `TournamentRepository` - Tournament lifecycle and queries
- `RegistrationRepository` - Player registration and sequence IDs
- `MatchRepository` - Match results and tournament progress
- And more...

### Backend Selection Guide
- **Mock**: Unit testing, development, API prototyping
- **Local JSON**: Single-user tournaments, version control, backup/restore
- **Database**: Multi-user production, concurrent access, advanced queries

## Current Implementation Status

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

## Next Steps
1. Complete FastAPI server implementation
2. Add authentication and authorization
3. Build TUI framework consuming API
4. Implement Swiss tournament logic
5. Add Discord bot integration
6. Production deployment setup
