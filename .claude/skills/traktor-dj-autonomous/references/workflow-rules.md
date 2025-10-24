# Professional DJ Workflow Rules

**Source**: Validated by 33-year veteran professional DJ
**Status**: ✅ Production rules - MUST be followed

## Core Principles

All autonomous DJ code MUST follow these rules. Violations result in:
- Audio bleed
- Volume spikes
- Unprofessional transitions
- Loss of crowd energy

## Rule #1: MASTER vs SYNC Decision Logic

### First Track (Empty Session)

When NO deck is currently playing:

```python
✅ DO:
- Set MASTER = ON
- Set SYNC = OFF (nothing to sync to yet)
- Set Volume = 85%
- Position crossfader to deck side (A → LEFT, B → RIGHT)
- THEN press play

❌ DO NOT:
- Enable SYNC on first track
- Start with low volume
- Press play before crossfader positioned
```

**Example Implementation**:
```python
def play_first_track(deck: str):
    # Configure mixer FIRST
    set_crossfader_position('left' if deck == 'A' else 'right')
    set_volume(deck, 85)
    
    # Set deck state
    set_master(deck, True)
    set_sync(deck, False)  # Nothing to sync to yet
    
    # NOW play
    play_deck(deck)
```

### Second Track Onwards (With Playing Deck)

When at least ONE deck is currently playing:

```python
✅ DO:
- Set MASTER = OFF (AUTO mode handles this)
- Set SYNC = ON (matches to playing deck's BPM)
- Start with Volume = 0-20%
- Position crossfader away from this deck
- Press play
- Gradually increase volume during transition

❌ DO NOT:
- Manually set MASTER (AUTO handles transfer)
- Start with high volume
- Disable SYNC
```

**Example Implementation**:
```python
def play_second_track(deck: str, playing_deck: str):
    # Configure mixer FIRST
    opposite_side = 'right' if playing_deck == 'A' else 'left'
    # Crossfader stays on playing deck initially
    set_volume(deck, 10)  # Start low
    
    # Set deck state
    set_master(deck, False)  # AUTO will handle
    set_sync(deck, True)     # Sync to playing deck
    
    # NOW play
    play_deck(deck)
```


## Rule #2: Pre-Playback Mixer Setup

**CRITICAL**: ALWAYS configure mixer BEFORE pressing play

### The Setup Sequence

```python
def setup_before_play(deck: str, is_first_track: bool):
    """
    Configure ALL mixer settings BEFORE play command
    """
    # Step 1: Crossfader position
    if is_first_track:
        position = 'left' if deck == 'A' else 'right'
    else:
        # Keep on currently playing deck
        position = get_crossfader_position()
    
    set_crossfader_position(position)
    
    # Step 2: Volume fader
    volume = 85 if is_first_track else 10
    set_volume(deck, volume)
    
    # Step 3: EQ to neutral (12 o'clock = 64)
    set_eq(deck, 'low', 64)
    set_eq(deck, 'mid', 64)
    set_eq(deck, 'high', 64)
    
    # Step 4: NOW safe to play
    play_deck(deck)
```

### Why This Matters

❌ **Wrong Order** (play first, then setup):
```python
play_deck('A')           # ← Audio bleed starts immediately!
set_volume('A', 85)      # ← Too late, already playing loud
set_crossfader('left')   # ← Sudden volume change
```

✅ **Correct Order** (setup first, then play):
```python
set_crossfader('left')   # ← Silent setup
set_volume('A', 85)      # ← Fader ready
play_deck('A')           # ← Clean start
```

## Rule #3: AUTO Mode Behavior

Traktor's AUTO mode is ENABLED by default. Understanding it is critical.

### How AUTO Mode Works

1. **Monitors volume faders continuously**
2. **Highest volume fader = MASTER deck**
3. **Automatic MASTER transfer during transitions**

### During Transitions

```python
# Initial state
Deck A: Playing, Volume 85%, MASTER = ON
Deck B: Playing, Volume 10%, SYNC = ON

# As you transition (crossfade)
# Volume changes trigger AUTO mode:

Deck A: Volume 75% → Still MASTER
Deck B: Volume 30% → Still SYNC

Deck A: Volume 60% → Still MASTER
Deck B: Volume 60% → Still MASTER (equal, no change yet)

Deck A: Volume 40% → MASTER transfers to B!
Deck B: Volume 75% → Now MASTER

# AUTO mode handled the transfer automatically
```


### Implementation Implications

```python
❌ DO NOT manually toggle MASTER during transitions:
def bad_transition(from_deck, to_deck):
    increase_volume(to_deck, 85)
    set_master(to_deck, True)    # ← WRONG! AUTO handles this
    decrease_volume(from_deck, 20)
    set_master(from_deck, False) # ← WRONG! Redundant

✅ DO let AUTO mode handle MASTER transfer:
def good_transition(from_deck, to_deck):
    increase_volume(to_deck, 85)     # AUTO sees volume increase
    # AUTO automatically transfers MASTER to to_deck
    decrease_volume(from_deck, 20)   # Finish transition
```

## Rule #4: Energy Flow Management

### Energy Levels (Validated Scale)

```
Energy 1-2:   Opening (118-122 BPM) - Warm up crowd
Energy 3-5:   Build-up (122-126 BPM) - Increase engagement
Energy 6-8:   Peak (126-130 BPM) - Maximum energy
Energy 9-10:  Climax (130+ BPM) - Brief peaks only
Energy 2-4:   Cool-down (122-126 BPM) - Wind down
```

### Set Structure (2-hour example)

```
0-30 min:   Opening (Energy 2-4, 118-122 BPM)
30-90 min:  Peak (Energy 6-8, 126-130 BPM)
90-120 min: Closing (Energy 3-5, 122-126 BPM)
```

### Track Selection Rules

1. **BPM Compatibility**: ±6 BPM for harmonic mixing
2. **Energy Progression**: ±1-2 levels per track (gradual changes)
3. **Key Compatibility**: Use Camelot wheel or mixed-in-key
4. **Genre Coherence**: Maintain consistent vibe within set sections

## Rule #5: Transition Timing

### Phrase-Perfect Mixing

```python
# Wait for phrase boundary (typically 8, 16, or 32 bars)
def wait_for_phrase_boundary(deck: str, bars: int = 32):
    """
    Wait until deck reaches phrase boundary
    """
    while True:
        position = get_playback_position(deck)
        bars_remaining = position.bars_until_phrase(bars)
        
        if bars_remaining <= 4:  # Prepare in last 4 bars
            return True
        
        time.sleep(0.5)  # Check every 500ms
```

### Transition Duration

- **Quick mix**: 16-32 bars (30-60 seconds)
- **Standard mix**: 32-64 bars (60-120 seconds)
- **Long mix**: 64+ bars (2+ minutes) - for build-ups

## Rule #6: EQ Management During Transitions

### The EQ Swap Technique

```python
def eq_swap_transition(from_deck, to_deck):
    """
    Professional EQ management during transition
    """
    # Start of transition
    start_transition()
    
    # Gradually reduce bass on outgoing deck
    for step in range(64, 0, -8):  # 64 down to 0
        set_eq(from_deck, 'low', step)
        time.sleep(0.5)
    
    # Simultaneously bring in bass on incoming deck
    for step in range(0, 64, 8):  # 0 up to 64
        set_eq(to_deck, 'low', step)
        time.sleep(0.5)
    
    # Complete crossfade
    complete_transition()
```


## Rule #7: Error Recovery

### Deck State Conflicts

**Problem**: Both decks show MASTER active

```python
def fix_master_conflict():
    """
    Only ONE deck should be MASTER at a time
    """
    state_a = get_deck_state('A')
    state_b = get_deck_state('B')
    
    if state_a['master'] and state_b['master']:
        # Both are MASTER - conflict!
        # Keep the one with higher volume as MASTER
        if state_a['volume'] > state_b['volume']:
            set_master('B', False)
        else:
            set_master('A', False)
```

### Audio Bleed

**Problem**: Sound from wrong deck

```python
def stop_audio_bleed(deck: str):
    """
    Emergency stop for audio bleed
    """
    # Immediate volume cut
    set_volume(deck, 0)
    
    # Move crossfader away
    position = 'right' if deck == 'A' else 'left'
    set_crossfader_position(position)
    
    # Then investigate and fix root cause
```

## Rule #8: Beatmatching and Sync

### When SYNC is Enough

```python
✅ SYNC handles:
- BPM matching (91.00 vs 91.52 → automatically compensated)
- Phase alignment (if both tracks have good beatgrids)
- Real-time tempo adjustments

❌ SYNC does NOT handle:
- Phrase alignment (you must cue to correct phrase boundary)
- Key/harmonic mixing (you must select compatible keys)
- Energy flow (you must manage progression)
```

### Manual Beatmatching (if needed)

```python
def manual_beatmatch(deck: str, reference_deck: str):
    """
    Fine-tune BPM match if SYNC is disabled
    """
    ref_bpm = get_bpm(reference_deck)
    current_bpm = get_bpm(deck)
    
    if current_bpm < ref_bpm:
        adjust_tempo(deck, +0.1)  # Speed up slightly
    elif current_bpm > ref_bpm:
        adjust_tempo(deck, -0.1)  # Slow down slightly
```

## Validation Checklist

Before any playback operation, verify:

```python
def validate_before_play(deck: str, is_first_track: bool):
    """
    Pre-flight checks before pressing play
    """
    checks = []
    
    # Check 1: Deck has track loaded
    if not deck_has_track(deck):
        checks.append("❌ No track loaded")
    else:
        checks.append("✅ Track loaded")
    
    # Check 2: MASTER/SYNC correctly configured
    if is_first_track:
        master_ok = get_master(deck) == True
        sync_ok = get_sync(deck) == False
    else:
        master_ok = get_master(deck) == False
        sync_ok = get_sync(deck) == True
    
    if master_ok and sync_ok:
        checks.append("✅ MASTER/SYNC configured")
    else:
        checks.append("❌ MASTER/SYNC incorrect")
    
    # Check 3: Mixer positioned correctly
    crossfader_ok = verify_crossfader_position(deck, is_first_track)
    if crossfader_ok:
        checks.append("✅ Crossfader positioned")
    else:
        checks.append("❌ Crossfader not positioned")
    
    # Check 4: Volume appropriate
    volume = get_volume(deck)
    if is_first_track:
        volume_ok = volume >= 75 and volume <= 95
    else:
        volume_ok = volume >= 0 and volume <= 30
    
    if volume_ok:
        checks.append("✅ Volume correct")
    else:
        checks.append("❌ Volume incorrect")
    
    # Print report
    for check in checks:
        print(check)
    
    return all("✅" in check for check in checks)
```

## Summary

**Key Takeaways:**

1. First track: MASTER=ON, SYNC=OFF, Volume=85%
2. Subsequent tracks: MASTER=OFF (AUTO), SYNC=ON, Volume=10%
3. ALWAYS configure mixer BEFORE pressing play
4. Let AUTO mode handle MASTER transfer during transitions
5. Follow energy flow guidelines for set progression
6. Use phrase-perfect timing for professional transitions
7. Manage EQ during transitions (bass swap technique)
8. Validate state before every operation

**Remember**: These rules are validated by 33 years of professional DJ experience. Following them ensures professional-quality performance.

---

**Version**: 1.0.0
**Last Updated**: 2025-10-23  
**Validation**: ✅ Professional DJ approved
