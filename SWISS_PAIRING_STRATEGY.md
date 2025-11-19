# Swiss Pairing Algorithm Strategy

*AIA PAI Hin R Claude Code [Sonnet 4.5] v1.0*

This document tracks design decisions for the Swiss tournament pairing algorithm implementation.

---

## Overview

Swiss pairing is a non-elimination tournament format where:
- Players are paired each round based on their current standings
- Players with similar records face each other
- No player faces the same opponent twice
- Tournament continues for a fixed number of rounds
- Winner determined by final standings with tiebreakers

---

## Design Decisions

### ✅ **1. Round 1 Pairing Strategy** - DECIDED

**Decision**: Configurable pairing with two modes

#### **Seeded Mode**
- Players paired based on initial rankings/sequence IDs
- Deterministic outcome (reproducible)
- Example: Player #1 vs Player #2, Player #3 vs Player #4, etc.
- Use case: Tournaments with established player rankings

#### **Random Mode**
- Players randomly shuffled before pairing
- Non-deterministic outcome
- **Re-issuable**: TO can regenerate Round 1 pairings for different matchups
- Use case: Kitchen table tournaments, casual play, fresh pairings

**Configuration**:
```python
component.config = {
    "round1_pairing_mode": "random",  # or "seeded"
    "allow_round1_reissue": True,     # Enable re-pairing before round starts
}
```

**Rationale**: Flexibility for different tournament styles. Kitchen table events benefit from randomness and re-issue capability, while competitive events may prefer seeded consistency.

---

### ❓ **2. Bye Assignment** - UNDER DISCUSSION

When an odd number of players requires one player to receive a bye, who should get it?

#### **Option A: Lowest Match Points Only**
- Player with fewest match points receives bye
- Simple, straightforward logic
- **Issue**: Same player could get multiple byes in a row if they keep losing

#### **Option B: Prioritize Bye Rotation**
- Track bye history, give to player who hasn't received one
- Only fall back to match points if all players have equal bye counts
- **Issue**: Could give bye to a top player early on

#### **Option C: Combination (Recommended for MTG)**
- First priority: Players with 0 byes received
- Second priority: Lowest match points among those with 0 byes
- Third priority: If all have 1+ byes, give to lowest match points
- **Advantage**: Fair distribution while respecting standings

**Proposed Decision**: **Option C** with configuration override

```python
component.config = {
    "bye_priority": "rotate_then_standings",  # or "standings_only", "rotate_strict"
}
```

**Questions**:
- Should there be a hard cap on byes (e.g., max 1 bye per player in a 4-round tournament)?
- How to handle bye assignment when multiple players have same points AND same bye count?

---

### ❓ **3. Pair-Down Strategy** - UNDER DISCUSSION

When the top player in a bracket has faced all other players at their level, they must "pair down" to a lower bracket.

#### **Option A: Next Bracket Down Only**
- 3-0 player pairs with highest-ranked 2-1 player
- Simple logic, minimal disruption
- **Issue**: Could create impossible pairings in complex scenarios

#### **Option B: Multi-Level Pair Down**
- Try next bracket, then next if still blocked
- 3-0 → 2-1 → 1-2 → 0-3 until valid pairing found
- **Advantage**: Handles complex scenarios gracefully

#### **Option C: Pair Down with History Tracking**
- Prioritize players who haven't paired down yet
- Among candidates, choose player with best tiebreakers
- **Advantage**: Fairest distribution of "unfavorable" pairings

**Proposed Decision**: **Option B** (multi-level) for robustness

```python
# Algorithm: Try each bracket level until valid pairing found
for bracket_level in [same_points, same_points - 3, same_points - 6, ...]:
    candidates = get_unpaired_players_at_level(bracket_level)
    candidates = filter(lambda p: not has_played(top_player, p), candidates)
    if candidates:
        return pair(top_player, best_candidate(candidates))
```

**Questions**:
- Should pair-down be recorded/tracked for tiebreaker purposes?
- Maximum pair-down distance (e.g., don't pair 3-0 with 0-3)?

---

### ❓ **4. Tiebreaker Application** - UNDER DISCUSSION

Tiebreakers (OMW%, GW%, OGW%) are used to rank players with identical match points.

#### **Usage Scenarios**:

**A) Final Standings Display**
- Always use tiebreakers for final tournament rankings
- Determines prizes, Top 8 cut, etc.
- **Consensus**: Required for tournament completion

**B) Pairing Order Within Bracket**
- When pairing 4 players at 2-1, should we sort them by OMW% first?
- Could affect quality of matchups
- **Question**: Does tiebreaker order within bracket matter for pairing?

**C) Bye Assignment Tiebreaker**
- If 2 players have same points and same bye count, use OMW% to decide?
- Or random selection?

**Proposed Decision**:
- ✅ **Final standings**: Always use full tiebreaker sequence
- ❓ **Pairing order**: Use tiebreakers to sort within bracket (better matchups)
- ❓ **Bye selection**: Use tiebreakers as final tiebreaker

**Tiebreaker Sequence (MTG Standard)**:
1. Match Points (higher is better)
2. Opponent Match Win % (OMW%) - higher is better
3. Game Win % (GW%) - higher is better
4. Opponent Game Win % (OGW%) - higher is better

**Floor Values** (per MTG rules):
- MW% and OMW% floor: 33.33% (even 0-X records = 0.3333)
- GW% and OGW% floor: 33.33%

---

### ❓ **5. Error Handling - Impossible Pairings** - UNDER DISCUSSION

In rare cases, valid pairings may become impossible (e.g., 3 players at 3-0 who have all played each other).

#### **Option A: Force Rematch (Least Recent)**
- Pair players who faced each other earliest in tournament
- Technically breaks "no rematch" rule
- **Use case**: Keep tournament running without TO intervention

#### **Option B: Assign Emergency Bye**
- Give one player a bye (even if even player count)
- Maintain no-rematch integrity
- **Issue**: Extra byes distort standings

#### **Option C: Require TO Intervention**
- Algorithm raises `ImpossiblePairingError`
- TO manually resolves (forced bye, manual pairing, etc.)
- **Advantage**: Preserves algorithm integrity, TO makes final call

**Proposed Decision**: **Option C** with clear error messages

```python
class ImpossiblePairingError(Exception):
    """Raised when valid pairings cannot be generated."""

    def __init__(self, message: str, players: list[Player], suggestions: list[str]):
        self.players = players
        self.suggestions = suggestions  # Suggested resolutions for TO
        super().__init__(message)
```

**Questions**:
- Should algorithm attempt backtracking (undo recent pairings to find solution)?
- Should we provide "suggested resolutions" with the error?

---

### ❓ **6. Match Structure for Byes** - UNDER DISCUSSION

How should bye matches be recorded in the database?

#### **Structure**:
```python
Match(
    player1_id=<player_receiving_bye>,
    player2_id=None,  # Indicates bye
    player1_wins=X,   # How many wins?
    player2_wins=0,
    draws=0,
)
```

#### **Win Count for Byes**:

**Option A: Always 2-0 (BO3 Standard)**
- Bye = 2 game wins, 0 losses
- Consistent with Best-of-3 default
- **Issue**: Incorrect for BO1 formats

**Option B: Format-Aware**
- BO1 format: 1-0
- BO3 format: 2-0
- BO5 format: 3-0
- **Advantage**: Accurate game win percentage calculations

**Option C: Configurable Per Tournament**
```python
component.config = {
    "bye_game_wins": 2,  # Configurable
}
```

**Proposed Decision**: **Option B** (format-aware) with Option C (configurable) override

**Match Points for Byes**:
- ✅ Always 3 points (same as match win)
- Standard across all formats

**Questions**:
- Should byes count toward OMW% calculations for opponents?
- Currently in MTG: Byes are excluded from opponent calculations

---

## Pairing Algorithm Workflow

### **Round 1 Pairing**
```
1. Get all active registrations
2. Check component config for pairing mode (seeded/random)
3. If seeded: Sort by sequence_id
4. If random: Shuffle players
5. Pair adjacent players (1v2, 3v4, 5v6, ...)
6. If odd player count: Last player receives bye
7. Generate Match objects
8. Return pairings
```

### **Subsequent Round Pairing (Round 2+)**
```
1. Calculate current standings (match points + tiebreakers)
2. Get all active players (exclude dropped)
3. Group players by match points (point brackets)
4. For each bracket (highest to lowest):
   a. Get unpaired players in bracket
   b. Sort by tiebreakers (OMW%, GW%, OGW%)
   c. While unpaired players in bracket:
      - Take top unpaired player
      - Find valid opponent (not previously played)
      - If no valid opponent in bracket:
        * Attempt pair-down to next bracket
      - Create pairing
5. If odd total players: Assign bye to lowest-ranked unpaired player
6. Generate Match objects
7. Verify no rematches (sanity check)
8. Return pairings
```

### **Bye Assignment Algorithm**
```
1. Get all unpaired players
2. Filter: Only players who have received 0 byes
3. If multiple candidates:
   - Sort by match points (ascending - lowest first)
   - Then by tiebreakers if needed
4. If no players with 0 byes:
   - Get players with fewest byes received
   - Sort by match points (ascending)
5. Return lowest-ranked player
6. Generate bye Match object
```

---

## Data Requirements

### **Standings Calculation**
For each player, compute:
```python
@dataclass
class PlayerStanding:
    player_id: UUID
    match_points: int           # 3 per win, 1 per draw, 0 per loss
    matches_played: int
    matches_won: int
    matches_lost: int
    matches_drawn: int
    game_wins: int
    game_losses: int
    game_draws: int
    byes_received: int          # Count of bye matches

    # Tiebreakers
    match_win_percentage: float    # MW% with 0.3333 floor
    game_win_percentage: float     # GW% with 0.3333 floor
    opponent_match_win_percentage: float  # OMW% - average of opponents' MW%
    opponent_game_win_percentage: float   # OGW% - average of opponents' GW%

    # Metadata
    opponents_faced: list[UUID]   # For rematch prevention
```

### **Match History Tracking**
Need to efficiently query:
- "Has Player A played Player B?" - O(1) lookup
- "Who has Player A played?" - List of opponent IDs
- "Player A's opponents' records" - For OMW% calculation

**Proposed Structure**:
```python
# Build match history dictionary during standings calculation
match_history: dict[UUID, set[UUID]] = {}
# match_history[player_id] = {opponent1_id, opponent2_id, ...}
```

---

## Configuration Schema

Component-level Swiss configuration:
```python
{
    "type": "swiss",
    "config": {
        # Round 1 behavior
        "round1_pairing_mode": "random",      # "random" | "seeded"
        "allow_round1_reissue": True,         # Can re-pair R1 before start

        # Bye handling
        "bye_priority": "rotate_then_standings",  # "standings_only" | "rotate_strict"
        "bye_game_wins": 2,                   # Game wins awarded for bye (or "auto" for format-based)
        "max_byes_per_player": None,          # Optional cap (None = unlimited)

        # Pairing behavior
        "use_tiebreakers_for_pairing": True,  # Sort within brackets by OMW%
        "allow_pair_down": True,              # Enable pairing down brackets
        "max_pair_down_distance": None,       # Max point gap (None = unlimited)

        # Error handling
        "impossible_pairing_strategy": "error",  # "error" | "force_rematch" | "emergency_bye"
    }
}
```

---

## Test Coverage

See `tests/test_swiss_pairing.py` for comprehensive test scenarios:

- ✅ Round 1 pairing (even/odd players, seeded/random)
- ✅ Subsequent round pairing (standings-based, no rematches)
- ✅ Bye handling (rotation, lowest-ranked, structure)
- ✅ Player state changes (drops, late entries)
- ✅ Tiebreaker calculations (MW%, GW%, OMW%, OGW%)
- ✅ Edge cases (impossible pairings, minimum size, etc.)
- ✅ Full tournament integration tests

**Total Test Cases**: 23 scenarios across 7 categories

---

## Open Questions for Resolution

1. **Bye Assignment**: Exact priority when points and bye count are equal?
2. **Pair-Down Tracking**: Should we record who paired down for fairness?
3. **Tiebreaker Usage**: Use OMW% for pairing order within brackets?
4. **Impossible Pairings**: Attempt backtracking before raising error?
5. **Bye in OMW%**: Should byes count in opponent calculations? (MTG: No)
6. **Rematch Prevention**: Store as set per player or global match history?

---

## Implementation Phases

### **Phase 1: Core Pairing** (First PR)
- [ ] Round 1 pairing (random mode only)
- [ ] Basic standings calculation (points only, no tiebreakers)
- [ ] Round 2+ pairing (simple bracket-based)
- [ ] No rematch validation
- [ ] Basic bye handling (lowest points)
- [ ] 5-8 passing tests

### **Phase 2: Tiebreakers** (Second PR)
- [ ] MW% and GW% calculations with floors
- [ ] OMW% and OGW% calculations
- [ ] Standings sort with full tiebreaker sequence
- [ ] Use tiebreakers for bye selection
- [ ] 8-12 passing tests

### **Phase 3: Advanced Pairing** (Third PR)
- [ ] Seeded Round 1 mode
- [ ] Round 1 re-issue capability
- [ ] Pair-down logic (multi-level)
- [ ] Bye rotation tracking
- [ ] Player drops/late entry handling
- [ ] 15-20 passing tests

### **Phase 4: Edge Cases & Polish** (Fourth PR)
- [ ] Impossible pairing detection and error handling
- [ ] Configuration validation
- [ ] Performance optimization (large tournaments)
- [ ] All 23 tests passing
- [ ] Documentation and examples

---

## Quick Reference: Outstanding Questions

**Need decisions on the following before full implementation:**

### **Q1: Bye Assignment Priority** ✅ DECIDED
When multiple players have same points AND same bye count:
- ~~A) Random selection?~~
- ~~B) Use tiebreakers (OMW%, GW%)?~~
- ~~C) Earlier registration time (sequence_id)?~~

**DECISION**: **Option A - Random selection**

---

### **Q2: Bye Cap** ✅ DECIDED
Should there be a maximum byes per player?
- ~~Example: Max 1 bye in a 4-round tournament~~
- ~~Or: Unlimited byes (could happen with odd count + drops)~~

**DECISION**: **Max 1 bye per player (configurable)**

Configuration:
```python
component.config = {
    "max_byes_per_player": 1,  # Default: 1, set to None for unlimited
}
```

---

### **Q3: Tiebreaker Sequence** ✅ DECIDED
How should tiebreakers be applied for both pairing and final standings?

**DECISION**: **Configurable tiebreaker sequence, consistent for entire tournament**

The same tiebreaker sequence is used for:
- Pairing order within point brackets
- Final standings display
- Bye assignment (when points/bye count are tied)

**Standard Tiebreaker Profiles**:

#### **Opponent-Heavy** (Default)
```python
tiebreaker_sequence = ["match_points", "omw_percent", "ogw_percent", "gw_percent", "random"]
```
- Match Points (primary)
- OMW% (Opponent Match Win %)
- OGW% (Opponent Game Win %)
- GW% (Game Win %)
- Random (final tiebreaker)
- **Rationale**: Maximizes emphasis on opponent quality over personal performance

#### **MTG Standard** (Alternative)
```python
tiebreaker_sequence = ["match_points", "omw_percent", "gw_percent", "ogw_percent", "random"]
```
- Official Wizards of the Coast tournament tiebreaker order
- OMW% → GW% → OGW%

#### **Personal Performance** (Alternative)
```python
tiebreaker_sequence = ["match_points", "gw_percent", "omw_percent", "ogw_percent", "random"]
```
- Emphasizes personal game wins over opponent strength

#### **Custom** (Configurable)
Tournament can define any sequence:
```python
component.config = {
    "tiebreaker_profile": "opponent_heavy",  # Default, or "mtg_standard", "personal_performance", "custom"
    "custom_tiebreaker_sequence": None,  # Only used when profile="custom"
}

# Example custom sequence:
component.config = {
    "tiebreaker_profile": "custom",
    "custom_tiebreaker_sequence": ["match_points", "gw_percent", "omw_percent", "ogw_percent", "random"],
}
```

**Note**: Within same-point brackets, "match_points" is already equal, so the next tiebreaker (OMW%, GW%, etc.) is used for ordering.

---

### **Q4: Pair-Down Tracking** ✅ DECIDED
Should we track when players "pair down"?

**DECISION**: **Yes, track pair-downs to distribute them fairly**

Implementation:
- Track which players have paired down in previous rounds
- When selecting who pairs down, prioritize players who haven't paired down yet
- Adds fairness to bracket movement

---

### **Q5: Impossible Pairing Resolution** ✅ DECIDED
When valid pairings can't be generated:

**DECISION**: **Error requiring TO intervention**

TO can manually:
- Force a specific pairing (override rematch restriction)
- Assign emergency bye
- Adjust tournament structure

---

### **Q6: Bye Structure by Format** ✅ DECIDED
Game wins awarded for bye:

**DECISION**: **Format-aware with configurable override**

- BO1 formats: 1-0 bye
- BO3 formats: 2-0 bye
- BO5 formats: 3-0 bye
- Configurable per tournament

---

### **Q7: Byes in OMW% Calculation** ✅ DECIDED
When calculating opponent statistics, should byes count?

**DECISION**: **Follow MTG standard - exclude byes from opponent calculations**

Byes do not count toward:
- Opponent Match Win Percentage (OMW%)
- Opponent Game Win Percentage (OGW%)

---

### **Q8: Rematch Prevention Data Structure** ✅ DECIDED
How to efficiently check "Have these players faced each other?"

**DECISION**: **Dict of sets for fast lookup**

```python
match_history: dict[UUID, set[UUID]] = {}
# match_history[player_id] = {opponent1_id, opponent2_id, ...}

# O(1) lookup:
has_played = opponent_id in match_history[player_id]
```

---

## References

- **MTG Tournament Rules**: [Wizards of the Coast Tournament Rules](https://wpn.wizards.com/en/resources/rules-documents/244)
- **Swiss Pairing Explanation**: Understanding OMW%, GW%, OGW% calculations
- **WER (Wizards Event Reporter)**: Reference implementation behavior
- **Tournament Director Data Model**: See `DATA_MODEL.md`

---

*Last Updated*: 2025-11-18
*Status*: Strategy in development, implementation pending
*Next Review*: After Phase 1 implementation
