# Swiss Tournament Impossible Pairing Scenarios

**AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0**

## Overview

In Swiss-system tournaments, an "impossible pairing" occurs when the remaining unpaired players have all played each other in previous rounds. This prevents the pairing algorithm from creating matches without rematches.

## When Does This Happen?

### Common Scenarios:

1. **Too Many Rounds for Player Count**
   - 4 players, 4+ rounds → Impossible after round 3 (everyone played everyone)
   - 8 players, 8+ rounds → Impossible in later rounds

2. **Multiple Player Drops Mid-Tournament**
   - Tournament starts with 16 players (4-5 rounds planned)
   - 8 players drop after round 2
   - Remaining 8 players may have impossible pairings in round 4+

3. **Small Tournaments with Uneven Brackets**
   - 5-7 players with many rounds
   - Bracket structure can lead to impossible pairings

## Tournament Organizer Actions

When impossible pairing is detected, the system provides guidance:

```
IMPOSSIBLE PAIRING in Round 4:
  4 unpaired players have all played each other already.
  Players: Player 1, Player 2, Player 3, Player 4

Tournament Organizer Actions:
  1. Consider ending Swiss rounds here and cutting to Top 8
  2. OR manually pair these players as rematches
  3. OR reduce total Swiss rounds for future tournaments
```

## Rematch Handling

The Tournament Director provides **two ways** to allow rematches when impossible pairings occur:

### Option 1: Tournament-Level Configuration

Set `allow_rematches: true` in tournament config (rare, most tournaments don't need this):

```python
config = {
    "standings_tiebreakers": ["omw", "gw", "ogw"],
    "allow_rematches": True  # Always allow rematches for this tournament
}

# Pairing will succeed even when impossible pairing would occur
pairings = pair_round(registrations, matches, component, config, round_number=4)
```

**When to use:**
- Small casual tournaments where rematches are acceptable
- Tournaments explicitly designed with more rounds than standard

### Option 2: Per-Round Override (Recommended)

Allow rematches for a specific round only (emergency situations):

```python
config = {
    "standings_tiebreakers": ["omw", "gw", "ogw"]
    # allow_rematches not set (defaults to False)
}

# Round 3 fails with impossible pairing error
try:
    pairings = pair_round(registrations, matches, component, config, round_number=4)
except ValueError as e:
    # TO decides to allow rematches for this round
    print(f"Impossible pairing detected: {e}")
    print("TO decision: Allow rematches for Round 4")

# Retry with override
pairings = pair_round(
    registrations,
    matches,
    component,
    config,
    round_number=4,
    allow_rematches_override=True  # Emergency override
)
```

**When to use:**
- Unexpected player drops create impossible pairing
- TO wants to complete one more round before cutting to top 8
- Emergency situations only (preserves tournament integrity)

## API/TUI Integration

### FastAPI Endpoint Example:

```python
@router.post("/tournaments/{tournament_id}/rounds/{round_number}/pair")
async def pair_round_endpoint(
    tournament_id: UUID,
    round_number: int,
    allow_rematches_override: bool = False,  # Optional query parameter
    data_layer: DataLayer = Depends(get_data_layer)
):
    try:
        pairings = pair_round(
            registrations,
            matches,
            component,
            config,
            round_number,
            allow_rematches_override=allow_rematches_override
        )
        return {"pairings": pairings}
    except ValueError as e:
        # Return helpful error to TO
        raise HTTPException(
            status_code=400,
            detail={
                "error": "impossible_pairing",
                "message": str(e),
                "suggested_actions": [
                    "End Swiss and cut to Top 8",
                    "Allow rematches by setting allow_rematches_override=true",
                    "Reduce rounds in future tournaments"
                ]
            }
        )
```

### TUI Example:

```python
# In tournament management screen:
try:
    pairings = pair_round(...)
except ValueError as e:
    # Show modal dialog to TO:
    modal = ImpossiblePairingDialog(
        error_message=str(e),
        actions=[
            ("End Tournament", end_tournament),
            ("Allow Rematches", lambda: pair_round(..., allow_rematches_override=True)),
            ("Cancel", close_dialog)
        ]
    )
    await modal.show()
```

## Rematch Logging

When rematches are created, the system logs warnings:

```
WARNING: Round 4: Creating 2 REMATCH pairings (allow_rematches enabled)
WARNING: Round 4: REMATCH created - Player seq#1 vs seq#3 (table 3)
WARNING: Round 4: REMATCH created - Player seq#2 vs seq#4 (table 4)
```

This ensures TOs are aware of rematches and can verify they're intentional.

## Prevention Strategies

### 1. Proper Round Count Planning

Use this formula for maximum Swiss rounds:
```
max_rounds = floor(log2(player_count)) + 1
```

Examples:
- 4 players → max 3 rounds
- 8 players → max 4 rounds
- 16 players → max 5 rounds
- 32 players → max 6 rounds

### 2. Tournament Structure

For tournaments with expected drops:
- Plan fewer rounds (leave margin for drops)
- Use Top 8 cut after Swiss
- Have clear drop policy (no drops after round X)

### 3. Minimum Player Validation

The system validates minimum players (2+) at tournament start:
```python
if len(active_players) < 2:
    raise ValueError("Tournament requires at least 2 players")
```

## Test Coverage

The rematch handling feature includes comprehensive tests:

1. **`test_impossible_pairing_raises_error`**
   - Verifies error is raised when rematches not allowed
   - Validates helpful TO guidance in error message

2. **`test_rematch_override_allows_pairing`**
   - Verifies `allow_rematches_override=True` works
   - Validates rematches are actually created

3. **`test_rematch_config_allows_pairing`**
   - Verifies tournament-level `allow_rematches` config
   - Validates pairing succeeds without override

## Implementation Details

### Hybrid Approach (Config + Override)

The system uses a **hybrid approach**:

```python
# Determine if rematches allowed
allow_rematches = (
    allow_rematches_override  # Per-round override takes precedence
    if allow_rematches_override is not None
    else config.get("allow_rematches", False)  # Fallback to tournament config
)
```

**Priority:**
1. `allow_rematches_override` parameter (if provided)
2. `config["allow_rematches"]` (if set)
3. Default: `False` (preserves tournament integrity)

### Rematch Pairing Algorithm

When rematches are allowed:
1. Pair unpaired players in standings order
2. Log warning for each rematch created
3. Return match objects as normal

This ensures rematches are:
- Clearly logged for TO review
- Paired in fair standings order
- Treated as normal matches for subsequent rounds

## References

- **Swiss Pairing Algorithm**: `src/swiss/pairing.py`
- **Test Cases**: `tests/test_swiss_pairing.py::TestImpossiblePairing`
- **Pairing Documentation**: `docs/SWISS_PAIRING.md` (future)

---

**Version:** 1.0
**Last Updated:** 2025-01-XX
**Maintained By:** Vibe-Coder Team
