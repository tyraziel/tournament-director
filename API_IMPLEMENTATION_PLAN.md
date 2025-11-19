# API Implementation Plan

**Created**: 2025-11-19
**Branch Strategy**: Incremental PRs for better review and testing
**AIA**: EAI Hin R Claude Code [Sonnet 4.5] v1.0

---

## 📊 Current Status (PR #1 - Ready to Ship)

**Branch**: `claude/review-and-plan-01WXpiX6GnyhEn5cvfWifc5k`
**Status**: ✅ Ready for PR

### What's Completed
- **30 API endpoints** (60% of v1.0 target)
- **65 tests** passing (100% success rate, 43% of v1.0 target)
- **9 tournament endpoints**: Full CRUD + filtering + lifecycle (start/complete)
- Full OpenAPI documentation
- Comprehensive integration tests

### Commits (6 total)
1. `254814a` - Add TournamentCreate and TournamentUpdate API models
2. `419ce7d` - Add tournament CRUD and lifecycle API endpoints
3. `4196489` - Add comprehensive tournament integration tests (11 tests)
4. `b6e57a8` - Add OpenAPI tests for tournament endpoints (3 tests)
5. `141f246` - Fix test isolation issue
6. `4bc4892` - Update documentation with tournament implementation status

### Files Changed
- **Created**: `src/api/routers/tournaments.py` (362 lines)
- **Modified**: `src/models/tournament.py` (added TournamentCreate, TournamentUpdate)
- **Modified**: `src/api/main.py` (registered tournament router)
- **Modified**: `tests/test_api_integration.py` (+259 lines)
- **Modified**: `tests/test_api_openapi.py` (+69 lines)
- **Modified**: `FASTAPI_STATUS.md` (updated metrics)

### Why Ship Now
✅ Clean, complete unit of work (Tournament CRUD + lifecycle)
✅ All 65 tests passing (100% success rate)
✅ Well-documented with updated FASTAPI_STATUS.md
✅ 6 focused commits with good messages
✅ Tournament creation and management is now functional
✅ Easy to review (~700 lines of new code)

---

## 🎯 Strategy: 2 More PRs to Complete Core API

Rather than one massive PR with all remaining work, we'll break it into **2 focused PRs**:

1. **PR #2**: Registration endpoints (simpler, high value)
2. **PR #3**: Rounds, pairings, and matches (complex but cohesive)

### Why This Approach?

**Benefits:**
- ✅ **Smaller, reviewable PRs** (easier to review and merge)
- ✅ **Incremental value delivery** (tournaments → registration → full Swiss system)
- ✅ **Better testing** (each PR can be tested independently)
- ✅ **Faster feedback loop** (merge registration quickly, then tackle complex stuff)
- ✅ **Lower risk** (if one part has issues, doesn't block everything)

**vs. One Massive PR:**
- ❌ Huge PR (~1000-1400 lines of new code)
- ❌ Hard to review (10+ new endpoints, 50+ tests)
- ❌ Risky to merge (if one part has issues, blocks everything)
- ❌ Slower iteration (more time before feedback)

---

## 📋 PR #2: Tournament Registration Endpoints

**Branch**: `claude/tournament-registration`
**Priority**: High
**Complexity**: Low-Medium
**Estimated Size**: ~300-400 lines, 15-20 tests

### Endpoints to Implement (3 endpoints)

```
POST   /tournaments/{id}/register        - Register player for tournament
GET    /tournaments/{id}/registrations   - List registrations (with status filter)
DELETE /tournaments/{id}/registrations/{player_id} - Drop player from tournament
```

### API Models Needed

**Request Models:**
```python
class PlayerRegistrationCreate(BaseModel):
    """Player registration request."""
    player_id: UUID
    notes: str | None = None
    # Optional: registration_password for password-protected tournaments
```

**Response Models:**
- Use existing `TournamentRegistration` model from `src/models/tournament.py`

### Implementation Details

**Register Player (`POST /tournaments/{id}/register`):**
- Validate tournament exists and is accepting registrations
- Check if player already registered (409 Conflict if duplicate)
- Assign next `sequence_id` using `get_next_sequence_id()`
- Set `registration_time` to current timestamp
- Default `status` to `PlayerStatus.ACTIVE`
- Return created `TournamentRegistration`

**List Registrations (`GET /tournaments/{id}/registrations`):**
- Support optional `status` query parameter (active, dropped, etc.)
- Pagination support (limit/offset)
- Return list of `TournamentRegistration` objects
- Include player details? (Consider adding player name via join)

**Drop Player (`DELETE /tournaments/{id}/registrations/{player_id}`):**
- Find registration by tournament_id + player_id
- Set `status` to `PlayerStatus.DROPPED`
- Set `drop_time` to current timestamp
- Return 204 No Content on success
- 404 if registration not found

### Test Coverage

**Integration Tests (~15 tests):**
1. Register player successfully
2. Register player - tournament not found (404)
3. Register player - already registered (409)
4. Register player - tournament already started (400?)
5. List registrations - empty tournament
6. List registrations - with players
7. List registrations - filter by status (active only)
8. List registrations - filter by status (dropped only)
9. List registrations - pagination
10. Drop player successfully
11. Drop player - not found (404)
12. Drop player - already dropped (idempotent)
13. Get registration by tournament and player
14. Late registration after tournament started
15. Registration respects max_players limit

**OpenAPI Tests (~2 tests):**
1. Validate registration endpoints documented
2. Validate TournamentRegistration schema

### Dependencies

**Data Layer:**
- `RegistrationRepository.create()` - ✅ Already exists
- `RegistrationRepository.list_by_tournament()` - ✅ Already exists
- `RegistrationRepository.get_by_tournament_and_player()` - ✅ Already exists
- `RegistrationRepository.update()` - ✅ Already exists
- `RegistrationRepository.get_next_sequence_id()` - ✅ Already exists

**No new data layer methods needed!**

### Business Logic to Consider

- **Registration window validation**: Check `registration.auto_open_time` and `auto_close_time`
- **Password protection**: If `registration.registration_password` is set, require it
- **Max players**: Enforce `registration.max_players` limit
- **Late registration**: Allow after tournament starts? (set late_entry flag?)
- **Bye loss assignment**: Late entries get bye losses for missed rounds

### Success Criteria

✅ 3 new registration endpoints working
✅ ~15-20 new tests passing
✅ Tournaments can accept player registrations
✅ Drop functionality works (sets status, preserves in standings)
✅ Sequence IDs assigned correctly
✅ OpenAPI documentation updated
✅ FASTAPI_STATUS.md updated (33 endpoints total)

---

## 📋 PR #3: Rounds, Pairings & Match Management

**Branch**: `claude/rounds-pairings-matches`
**Priority**: High
**Complexity**: High (integrates Swiss pairing algorithms)
**Estimated Size**: ~800-1000 lines, 30-40 tests

### Endpoints to Implement (7 endpoints)

```
# Round Management
POST   /tournaments/{id}/rounds/{n}/pair     - Generate pairings for round N
GET    /tournaments/{id}/rounds/{n}          - Get round details (with matches)
POST   /tournaments/{id}/rounds/{n}/complete - Mark round as complete, advance to next

# Match Management
GET    /tournaments/{id}/matches             - List all matches in tournament
GET    /matches/{id}                         - Get match details
PUT    /matches/{id}/result                  - Submit match result

# Standings
GET    /tournaments/{id}/standings           - Calculate and return current standings
```

### API Models Needed

**Request Models:**
```python
class MatchResultSubmit(BaseModel):
    """Match result submission."""
    winner_id: UUID | None = None  # None = draw
    player1_wins: int
    player2_wins: int
    draws: int = 0
    notes: str | None = None
```

**Response Models:**
- Use existing `Round`, `Match`, `Pairing` from `src/models/match.py`
- Create `StandingsEntry` model:

```python
class StandingsEntry(BaseModel):
    """Single entry in tournament standings."""
    rank: int
    player_id: UUID
    player_name: str  # Include for convenience
    sequence_id: int  # Player number (#1, #2, etc.)
    match_points: int
    game_points: int
    matches_played: int
    match_win_percentage: float
    game_win_percentage: float
    opponent_match_win_percentage: float
    opponent_game_win_percentage: float
```

### Implementation Details

**Generate Pairings (`POST /tournaments/{id}/rounds/{n}/pair`):**
- Validate tournament is IN_PROGRESS
- Validate round N doesn't already exist
- Get all registrations with ACTIVE status
- Import and use `src/swiss/pairing.py`:
  - Round 1: `pair_first_round()` (random pairing)
  - Round 2+: `pair_round()` (by standings with tiebreakers)
- Create `Round` object with status=ACTIVE
- Create `Match` objects for each pairing
- Handle byes (odd player count)
- Return round with pairings

**Get Round (`GET /tournaments/{id}/rounds/{n}`):**
- Find round by tournament_id + round_number
- Include all matches for this round
- Return Round with nested Match list
- 404 if round not found

**Complete Round (`POST /tournaments/{id}/rounds/{n}/complete`):**
- Validate all matches have results (end_time set)
- Use `src/lifecycle.py::is_round_complete()`
- Mark round as COMPLETED
- If not at max_rounds, optionally auto-create next round?
- Return updated round

**List Matches (`GET /tournaments/{id}/matches`):**
- List all matches for tournament (across all rounds)
- Optional filter by round_number query param
- Pagination support
- Return list of Match objects

**Get Match (`GET /matches/{id}`):**
- Get single match by ID
- Return Match object
- 404 if not found

**Submit Result (`PUT /matches/{id}/result`):**
- Validate match exists and is in ACTIVE round
- Update match with winner, games won/lost
- Set end_time to current timestamp
- Return updated Match

**Calculate Standings (`GET /tournaments/{id}/standings`):**
- Get all registrations (including ACTIVE and DROPPED)
- Get all completed matches
- Import and use `src/swiss/standings.py`:
  - `calculate_standings()` with tiebreaker chain
- Return list of StandingsEntry objects ordered by rank

### Integration with Existing Swiss Code

**Already Implemented (in `src/swiss/`):**
- ✅ `pairing.py::pair_first_round()` - Random pairing for Round 1
- ✅ `pairing.py::pair_round()` - Swiss pairing with standings
- ✅ `standings.py::calculate_standings()` - Full standings with tiebreakers
- ✅ `tiebreakers.py` - OMW%, GW%, OGW% calculations
- ✅ `lifecycle.py::is_round_complete()` - Round completion check
- ✅ `lifecycle.py::advance_to_next_round()` - Round advancement

**What We Need:**
- **Adapter layer**: Convert between API models and Swiss algorithm inputs
- **Match → Result conversion**: Swiss code uses `Match` model, needs game results
- **Player lookup**: Swiss code needs player objects from registrations

### Test Coverage

**Integration Tests (~30 tests):**

**Round Pairing (8 tests):**
1. Pair Round 1 - 8 players (4 pairings)
2. Pair Round 1 - 7 players (3 pairings + 1 bye)
3. Pair Round 2 - after results (by standings)
4. Pair Round 2 - no rematches enforced
5. Pair round - tournament not started (400)
6. Pair round - round already exists (409)
7. Pair round - insufficient players (400)
8. Get round details with matches

**Round Completion (5 tests):**
1. Complete round - all matches done
2. Complete round - matches incomplete (400)
3. Complete round - auto-advance to next round
4. Complete round - at max_rounds (tournament ends)
5. is_round_complete validation

**Match Management (8 tests):**
1. Submit match result - player 1 wins
2. Submit match result - player 2 wins
3. Submit match result - draw
4. Submit match result - match not found (404)
5. Submit match result - already has result (400)
6. Get match by ID
7. List matches for tournament
8. List matches filtered by round

**Standings (6 tests):**
1. Calculate standings - after Round 1
2. Calculate standings - after Round 2 (tiebreakers applied)
3. Calculate standings - with dropped player
4. Calculate standings - empty tournament
5. Standings include all tiebreakers (MW%, GW%, OMW%, OGW%)
6. Standings correctly ranked

**Full Tournament Flow (3 tests):**
1. Complete 8-player, 3-round tournament (create → register → pair → results → standings)
2. Tournament with bye rotation (7 players, 4 rounds)
3. Tournament with drops and late entries

**OpenAPI Tests (~3 tests):**
1. Validate round/pairing endpoints documented
2. Validate match endpoints documented
3. Validate StandingsEntry schema

### Dependencies

**Data Layer:**
- `RoundRepository.create()` - ✅ Already exists
- `RoundRepository.get_by_tournament_and_number()` - ✅ Already exists
- `RoundRepository.update()` - ✅ Already exists
- `MatchRepository.create()` - ✅ Already exists
- `MatchRepository.list_by_round()` - ✅ Already exists
- `MatchRepository.list_by_tournament()` - ✅ Already exists
- `MatchRepository.get_by_id()` - ✅ Already exists
- `MatchRepository.update()` - ✅ Already exists

**No new data layer methods needed!**

### Business Logic to Consider

- **Pairing validation**: No rematches (track via pairing history)
- **Bye assignment**: Rotate fairly, prefer lowest-ranked player
- **Drop handling**: Exclude from future pairings, include in standings
- **Late entry handling**: Assign bye losses for missed rounds
- **Match result validation**: Ensure winner is one of the two players
- **Auto-advance rounds**: Option to automatically create next round on completion
- **Tiebreaker configuration**: Which tiebreakers to use, in what order

### Success Criteria

✅ 7 new endpoints working (rounds, matches, standings)
✅ ~30-40 new tests passing
✅ Full tournament flow testable (create → register → pair → play → standings)
✅ Swiss pairing algorithms integrated via API
✅ Standings calculated with proper tiebreakers
✅ Round completion and advancement working
✅ OpenAPI documentation updated
✅ FASTAPI_STATUS.md updated (40 endpoints total, 80% of v1.0 target)

---

## 🎯 After These 3 PRs

### What We'll Have
- ✅ **40 endpoints** (80% of v1.0 target)
- ✅ **~110-120 tests** (73% of v1.0 target)
- ✅ **Complete Swiss tournament system** (create → register → pair → play → standings)
- ✅ **Full lifecycle management** (start, rounds, complete)
- ✅ **Production-ready core API**

### What's Still Needed for v1.0
- ❌ Authentication & authorization (~8 endpoints)
- ❌ API key management (~4 endpoints)
- ❌ WebSocket support for live updates
- ❌ Advanced features (batch operations, file uploads)

### Future PRs (Lower Priority)
- **PR #4**: Authentication & authorization (JWT + API keys)
- **PR #5**: WebSocket support for live tournament updates
- **PR #6**: Advanced features and optimizations

---

## 📝 Development Guidelines

### For Each PR

**Before Starting:**
1. ✅ Create new branch from main
2. ✅ Review this plan and FASTAPI_STATUS.md
3. ✅ Read relevant documentation (CLAUDE.md for TDD, SESSION_SUMMARY.md for context)

**During Development:**
1. ✅ Follow TDD methodology (Red-Green-Refactor)
2. ✅ Write tests FIRST, then implementation
3. ✅ Commit frequently (every completed feature)
4. ✅ Push after every 2-3 commits
5. ✅ Update FASTAPI_STATUS.md as you go

**Before Submitting PR:**
1. ✅ All tests passing (100% success rate)
2. ✅ OpenAPI tests updated
3. ✅ Integration tests comprehensive
4. ✅ FASTAPI_STATUS.md updated
5. ✅ Commit messages include AIA attribution
6. ✅ Run full test suite: `pytest tests/test_api_*.py -v`

### Test Coverage Standards

- **Minimum**: 85% overall coverage
- **Target**: 90% overall coverage
- **Each endpoint**: At least 3 tests (success, 404, validation error)
- **Each workflow**: End-to-end integration test

### Code Quality Standards

- ✅ Type hints on all functions
- ✅ Docstrings on all endpoints
- ✅ Proper HTTP status codes
- ✅ Async/await throughout
- ✅ Repository pattern (no direct data access)
- ✅ Error handling with proper exceptions

---

## 🔄 Context Reload Guide

If you need to start a new session and want to continue this work:

1. **Read this file** (`API_IMPLEMENTATION_PLAN.md`) - Complete roadmap
2. **Read `FASTAPI_STATUS.md`** - Current implementation status
3. **Read `SESSION_SUMMARY_FASTAPI.md`** - Previous session details
4. **Check current branch**: `git branch --show-current`
5. **Run tests**: `pytest tests/test_api_*.py -v` - Verify everything works
6. **Check which PR to work on**: See "Current Status" section above

---

**Next Steps:** Ship PR #1, then start PR #2 (Registration endpoints)

**AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0**

Vibe-Coder: Andrew Potozniak <vibecoder.1.z3r0@gmail.com>
Co-authored-by: Claude Code [Sonnet 4.5] <claude@anthropic.com>
