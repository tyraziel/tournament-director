# Tournament Director TUI - Vibe Coding Sessions

*AIA PAI Hin R Claude Code v1.0 // AIA Primarily AI, Human-initiated, Reviewed, Claude Code v1.0 // This work was primarily AI-generated. AI was prompted for its contributions, or AI assistance was enabled. AI-generated content was reviewed and approved. The following model(s) or application(s) were used: Claude Code.*

## Session 1: Requirements Planning & Architecture Design
**Date**: August 27, 2025  
**Start Time**: 21:41  
**Status**: 🔄 In Progress  

### 🎯 Session Goals
Plan out Tournament Director TUI requirements and design backend abstraction architecture for MTG tournament management.

### 🚀 Session Progress

#### Requirements Discovery (21:41 - 21:51)
- ✅ **Project Foundation**: Created CLAUDE.md with AI attribution and dual licensing
- ✅ **Backend Strategy**: Planned 3-backend abstraction (mock, local, server)
- ✅ **Security Planning**: JWT, rate limiting, IP allow/deny lists, RBAC
- 🔄 **Tournament Requirements**: Discussing MTG Swiss tournament structure
  - Swiss rounds with OMW%/GW%/OGW% tiebreakers
  - Cut to Top X (2/4/8) then single elimination
  - First-to-2 wins format with draws possible
  - Magic: The Gathering focus

#### Architecture Decisions Made
- **Repository Pattern**: Clean abstraction for swappable backends
- **Configuration-Driven Security**: JSON-based IP lists and rate limits
- **Test-First Design**: Mock backend for comprehensive testing
- **Migration Path**: Local → Server deployment strategy

### 🛠 Technologies Planned
- **Framework**: Python + Textual TUI (following MTGA TUI patterns)
- **Backend Options**: Mock (testing), Local (files), Server (API)
- **Security**: JWT auth, IP filtering, rate limiting
- **Data Models**: Pydantic validation throughout

### 🎮 Tournament Features Discussed
- Swiss pairing engine with tiebreakers
- Match result tracking (2-0, 2-1, draws)
- Standings calculations with OMW%/GW%/OGW%
- Cut to elimination rounds
- Discord bot integration potential

### 📁 Files Created This Session
- `CLAUDE.md` - Project documentation with architecture plans
- `VIBE-CODING.md` - This session tracking file

### 🎯 Next Steps
- Finalize tournament requirements and workflow
- Design core data models (Tournament, Player, Match, Round)
- Implement backend abstraction interfaces
- Build Swiss pairing algorithm
- Create TUI framework structure

### 💭 Session Notes
Great collaborative requirements discussion! The Swiss tournament structure with proper tiebreakers is the core complexity. Need to decide on pairing engine sophistication level and real-time vs batch processing approach.

#### Major Breakthrough: API-First Design (21:51+)
- ✅ **Tournament Simulations**: Use mock backend to run full tournament simulations
- ✅ **Tiebreaker Validation**: Test complex OMW%/GW%/OGW% edge cases with known scenarios  
- ✅ **Business Logic Testing**: Swiss pairing algorithms independent of TUI
- ✅ **Clean Architecture**: TUI becomes pure display layer consuming API
- ✅ **Future-Proof**: Same API serves TUI, Discord bot, web interface

### 🎯 Key Requirements Locked In
- **Multi-tournament management** with metadata and states
- **Dynamic Swiss structure** (adjustable rounds, cut sizes)
- **Player state management** (drop/add/undrop with bye losses)  
- **TO manual control** (result entry, pairing overrides)
- **Configuration system** (venues: Kitchen Table, Snack House, etc.)
- **API-first architecture** with three backend strategy

#### Sacred Pause (22:28)
The vibes demand a pause until 22:35. Pauper must be prioritized! 

#### Format Expansion Discussion (22:28)
- **Game Systems**: MTG, Pokemon, Star Wars Unlimited, NFL Five, [Custom TCG]
- **Base Format Categories**: CONSTRUCTED, PRE_CONSTRUCTED, LIMITED, SPECIAL
- **MTG Constructed**: **PAUPER** (priority!), Standard, Modern, Legacy, Vintage
- **MTG Limited**: Draft, Sealed, Dark Draft, Winston Draft, Solomon Draft
- **Pre-Constructed**: Challenger Decks, Championship Decks, Starter Products
- **Special Formats**: JumpStart (hybrid), house rules variants

**Design Decision**: Multi-game system support with hierarchical format structure

**Pause for vibes realignment** 🧘‍♂️

---
*Session paused at 22:28, resuming 22:35*
