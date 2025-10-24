# DJ Workflow Rules - Professional Best Practices

**Date Created**: 2025-10-07
**Source**: Real DJ (33 years experience) - Test 05 Session
**Status**: CRITICAL - All agents must follow these rules

---

## 🎯 Rule #1: AUTO Mode - Automatic MASTER Management (DEFAULT)

**CRITICAL UPDATE (2025-10-09)**: Traktor's AUTO mode (CC 56) is **ALWAYS ACTIVE** by default.

### How AUTO Mode Works:

**Automatic MASTER Transfer Based on Volume**:
- Deck with **highest volume fader** automatically becomes **MASTER**
- When transitioning: volume fader movements trigger AUTO MASTER transfer
- **No manual MASTER commands needed** during transitions (AUTO handles it)

**Workflow Example**:
```
Initial: Deck A volume 85% → AUTO sets Deck A as MASTER
Transition:
  - Deck A volume: 85% → 50% → 0%
  - Deck B volume: 0% → 50% → 85%
  - When Deck B volume > Deck A: AUTO transfers MASTER to Deck B
Final: Deck B volume 85% → AUTO sets Deck B as MASTER
```

**Key Benefits**:
- ✅ Automatic MASTER handoff during transitions
- ✅ No manual MASTER button presses needed
- ✅ Volume fader naturally controls who is MASTER
- ✅ Smooth, professional workflow

**Important Notes**:
- First track still needs manual MASTER (no reference yet)
- BPM differences (91.00 vs 91.52) are NORMAL - SYNC compensates automatically
- Manual MASTER override possible (disable AUTO) - covered in advanced workflows

---

## 🎯 Rule #2: MASTER vs SYNC Decision Logic (With AUTO Active)

**UPDATED WORKFLOW RULE**: With AUTO enabled, focus shifts to SYNC setup, not MASTER commands.

### Decision Tree (AUTO Mode Active):

```
BEFORE loading track:
├─ Check if ANY deck is currently playing
│
├─ NO deck playing? (First track of session)
│  └─> Set new track as MASTER ✅ (manual, AUTO has no reference yet)
│     └─> Set volume fader high (~85%) to maintain MASTER
│     └─> DO NOT enable SYNC (nothing to sync to)
│     └─> This becomes the tempo master
│
└─ YES, another deck is playing?
   ├─> Check if AUTO is active (should be ON by default)
   │
   ├─> AUTO is ON?
   │  └─> DO NOT manually set MASTER ❌ (AUTO will handle it)
   │  └─> Enable SYNC on new track ✅
   │  └─> SYNC will match BPM automatically (even if different: 91.00 vs 91.52)
   │  └─> Start with volume fader LOW (0-20%)
   │  └─> During transition: raise volume → AUTO transfers MASTER automatically
   │
   └─> AUTO is OFF? (rare, advanced workflow)
      └─> Follow manual MASTER logic (legacy workflow)
```

**Key Changes with AUTO**:
- Agents don't send MASTER commands during transitions
- Volume fader position = MASTER determinant
- SYNC compensates BPM differences (no perfect match needed)

---

## 📋 Detailed Scenarios

### Scenario 1: Starting a DJ Session (Empty Decks)

**Initial State**:
- All decks empty
- No audio playing
- No MASTER set

**Workflow**:
1. ✅ Load track to Deck A
2. ✅ Set Deck A as **MASTER** (it's the tempo reference)
3. ❌ Do NOT enable SYNC (nothing to sync to)
4. ✅ Prepare mixer (crossfader/volume)
5. ✅ Press PLAY

**Why MASTER not SYNC?**
- First track sets the tempo for the entire session
- SYNC needs a MASTER to sync to - none exists yet
- MASTER provides stable tempo reference

---

### Scenario 2: Loading Second Track (One Deck Playing) - AUTO MODE

**Initial State**:
- Deck A: Playing, volume 85%, AUTO set it as MASTER
- Deck B: Empty
- Audio output active
- AUTO: ON (default)

**Workflow**:
1. ✅ Load track to Deck B
2. ❌ Do NOT manually set Deck B as MASTER (AUTO will handle transfer)
3. ✅ Set Deck B volume fader LOW (0-20%) initially
4. ✅ Enable SYNC on Deck B (to match Deck A's tempo)
   - SYNC compensates BPM differences automatically (91.00 → 91.52 = no problem)
5. ✅ Cue/preview Deck B in headphones
6. ✅ Prepare mixer for transition (crossfader, EQ)
7. ✅ Press PLAY when ready to mix
8. ✅ During transition: raise Deck B volume → AUTO transfers MASTER automatically

**Why SYNC + AUTO, not manual MASTER?**
- AUTO manages MASTER based on volume fader position
- Deck B starts with low volume → stays non-MASTER
- As Deck B volume increases during mix → AUTO transfers MASTER
- As Deck A volume decreases → AUTO removes MASTER from Deck A
- Smooth, automatic handoff - no manual commands needed
- SYNC ensures perfect beatmatching even with BPM differences

---

### Scenario 3: Mid-Session Track Loading - AUTO MODE

**Initial State**:
- Deck A: Playing, volume 85%, AUTO set as MASTER, audience hearing it
- Deck B: Empty or previous track finished
- Crossfader positioned to Deck A
- AUTO: ON (default)

**Workflow**:
1. ✅ Check: Is Deck A playing? YES
2. ✅ Check: Is AUTO active? YES (should be)
3. ✅ Load new track to Deck B
4. ❌ Do NOT manually set MASTER on Deck B (AUTO will manage)
5. ✅ Set Deck B volume fader LOW (0-20%)
6. ✅ Enable SYNC on Deck B (BPM will auto-match via SYNC)
7. ✅ Cue point setup on Deck B
8. ✅ Crossfader ready (positioned to Deck A)
9. ✅ Start Deck B playback (low volume, inaudible to audience)
10. ✅ Begin transition:
    - Crossfader: A → Center → B
    - EQ: Bass swap (A down, B up)
    - **Volume**: A high → low, B low → high
    - AUTO automatically transfers MASTER from A to B during volume crossover

---

## 🎚️ Rule #2: Mixer Setup Before Playback

**CRITICAL**: Set mixer controls BEFORE pressing play, not after.

### Pre-Playback Checklist:

**For FIRST track (no audio playing)**:
1. ✅ Crossfader → Full LEFT (or full RIGHT for Deck B)
2. ✅ Playing deck volume fader → 80-100%
3. ✅ Silent deck volume fader → Can stay up (no audio yet)
4. ✅ EQ controls → Neutral (12 o'clock)

**Why move crossfader first?**
- Prevents audio bleed/volume spikes
- Clean, professional start
- Audience hears smooth intro

**Alternative approach** (also valid):
- Lower the SILENT deck's volume fader to 0%
- Keep crossfader center
- Raise volume when ready to bring in track

**User preference (from Test 05)**:
> "molti abbassano il fader e spostano il crossfader"
> (Many DJs lower the fader AND move the crossfader)

**Both approaches valid**:
- **Crossfader method**: Traditional DJ mixer approach
- **Fader method**: Club mixer / Traktor software approach
- **Combined**: Maximum control, safest option

---

## 🔊 Rule #3: Volume Fader Management

### Initial Setup:
- **Playing deck**: 75-85% (standard listening level)
- **Silent deck**: Can stay at 75-85% IF crossfader is positioned away
- **Silent deck**: Should be 0% IF crossfader is center

### During Transition:
- Gradually adjust faders to blend tracks
- Watch master output level (no clipping)
- Use EQ to create space in the mix

---

## 🎛️ Rule #4: Crossfader Positioning

### Standard Assignments (Traktor Default):
- **Deck A**: Crossfader LEFT (A-side)
- **Deck B**: Crossfader RIGHT (B-side)
- **Deck C**: Crossfader LEFT (A-side)
- **Deck D**: Crossfader RIGHT (B-side)

### Playing Single Deck:
- **Deck A solo**: Crossfader full LEFT
- **Deck B solo**: Crossfader full RIGHT
- **Both decks**: Crossfader CENTER (during mix)

### Transition Flow:
```
Deck A playing, loading Deck B:
├─ Crossfader: START at full LEFT ⬅️
├─ Load & cue Deck B
├─ Start Deck B playback (audience hears only A)
├─ Begin crossfade: LEFT → CENTER → RIGHT ➡️
└─ End: Crossfader full RIGHT (only B audible)
```

---

## 🤖 Agent Implementation Rules

### music-vision-navigator:
**NEW CAPABILITY (2025-10-08)**: Visual state verification via screenshot

**Visual Verification Protocol**:
1. Capture Traktor screenshot via Bash tool:
   ```bash
   screencapture -x /tmp/traktor_screen_$(date +%s).png
   ```
2. Load screenshot via Read tool (Claude multimodal analysis)
3. Extract visual state information
4. Provide JSON state report for other agents

**MUST extract before load/play**:
```json
{
  "any_deck_playing": true/false,
  "master_deck": "A"/"B"/"C"/"D"/null,
  "playing_decks": ["A", "B"],  // Lista di deck attualmente playing
  "deck_states": {
    "A": {
      "status": "playing"/"paused"/"stopped"/"empty",
      "track_name": "Track Title - Artist",
      "bpm": 128.00,
      "key": "8A",
      "master": true/false,
      "sync": true/false,
      "volume": 75  // 0-100%
    },
    "B": { /* similar */ },
    "C": { /* similar */ },
    "D": { /* similar */ }
  },
  "crossfader_position": "left"/"center"/"right",  // Visual estimate
  "crossfader_percentage": 0-100,  // If visible
  "master_volume": 80,  // 0-100% if visible
  "next_recommended_deck": "B",  // Based on analysis
  "workflow_compliant": true/false,
  "detected_issues": ["warning message if any"]
}
```

**When to Use Visual Verification**:
- ✅ Before loading first track (verify all decks empty)
- ✅ Before loading subsequent tracks (verify MASTER exists)
- ✅ When user requests "check Traktor state"
- ✅ Master-coordinator pre-operation verification
- ✅ After MIDI commands (verify they executed correctly)

### deck-control-agent:
**Decision logic**:
```python
if not any_deck_playing:
    # First track - set as MASTER
    controller.set_deck_master(new_deck, True)
    # Do NOT enable SYNC
else:
    # Another track playing
    if master_deck_exists:
        # Do NOT set new track as MASTER
        # Enable SYNC instead (optional, depends on workflow)
        controller.set_deck_sync(new_deck, True)
```

### mixer-control-agent:
**Pre-playback setup**:
```python
if first_track_of_session:
    # Move crossfader to playing deck's side
    if deck == DeckID.A:
        controller.set_crossfader(0.0)  # Full LEFT
    elif deck == DeckID.B:
        controller.set_crossfader(1.0)  # Full RIGHT

    # Optionally: lower silent deck volume
    # (if crossfader not moved)
```

---

## 📝 Notes from Real DJ (Test 05)

> "prima di caricare la traccia si fa attenzione se c'è un'altra traccia che sta suonando, se i volume e i cross-fader sono in posizione giusta"

**Translation**: Before loading a track, pay attention to whether another track is playing, and if volumes and crossfader are in the right position.

> "in questo caso bisogna mettere la traccia come 'master' perchè nessun'altra sta suonando"

**Translation**: In this case (no other track playing), you must set the track as 'master' because no other is playing.

> "se invece c'è già traccia che sta suonando ed è in 'master' non bisogna accenderlo ma al limite si accende il sync"

**Translation**: If instead there's already a track playing and it's 'master', you must NOT activate it (MASTER), but optionally you activate SYNC.

> "molto più comodo ma sono un 33enno che lavora con le cose che funzionano"

**Translation**: Much more convenient, but I'm a 33-year-old who works with things that work.

**Key Insight**: This is **production-tested workflow from a working DJ**. Not theoretical - this is how real DJs work.

---

## 🎯 Summary: Quick Reference (AUTO Mode Active)

| Situation | MASTER | SYNC | Volume Fader | Crossfader | Action |
|-----------|--------|------|--------------|------------|--------|
| **First track (empty session)** | ✅ Manual | ❌ Do NOT | High (85%) | Move to deck side | Play |
| **Second track (one playing)** | ❌ AUTO handles | ✅ Enable | Start LOW (0-20%) | Keep away from new deck | Cue → Mix → Volume up |
| **During transition** | ❌ AUTO handles | ✅ Keep active | Outgoing: high→low<br>Incoming: low→high | A → Center → B | AUTO transfers MASTER at crossover |
| **Post-transition** | ❌ AUTO handles | ✅ Active on new track | New deck HIGH (85%) | On new deck | New deck is MASTER (AUTO) |
| **Emergency stop** | Keep as-is | Keep as-is | Adjust as needed | Move to working deck | Troubleshoot |

**Key Principle with AUTO**:
- 📊 **Volume Fader = MASTER Determinant**
- 🔄 **AUTO transfers MASTER automatically** during volume crossover
- 🎛️ **Agents focus on**: SYNC setup, volume movements, crossfader, EQ
- ⛔ **Agents DON'T send**: Manual MASTER commands during transitions

---

## 🔧 Technical Implementation

### Check Deck States (Python):
```python
def should_set_master(controller, new_deck):
    """Determine if new deck should be MASTER"""
    # Check all decks for playing state
    any_playing = any([
        controller.is_deck_playing(DeckID.A),
        controller.is_deck_playing(DeckID.B),
        controller.is_deck_playing(DeckID.C),
        controller.is_deck_playing(DeckID.D)
    ])

    if not any_playing:
        # No deck playing - new deck should be MASTER
        return True
    else:
        # Another deck playing - do NOT set as MASTER
        return False

def prepare_deck_for_playback(controller, deck, is_first_track):
    """Complete deck preparation workflow"""
    if is_first_track:
        # Set as MASTER (tempo reference)
        controller.set_deck_master(deck, True)

        # Position crossfader
        if deck == DeckID.A:
            controller.set_crossfader(0.0)  # Full LEFT
        elif deck == DeckID.B:
            controller.set_crossfader(1.0)  # Full RIGHT

        # Start playback
        controller.play_deck(deck)
    else:
        # Enable SYNC (optional)
        controller.set_deck_sync(deck, True)

        # Keep crossfader away from new deck
        # DJ will manually transition when ready

        # Start playback (cued, ready to mix)
        controller.play_deck(deck)
```

---

## 🎓 Why This Matters

**For AI Agents**:
- Following human DJ workflow makes output predictable
- Matches what users expect from DJ software
- Prevents audio mishaps (volume spikes, tempo chaos)
- Creates professional, smooth mixes

**For Users**:
- System behaves like a human DJ
- No surprises or unexpected behavior
- Can trust the automation
- Can step in and take manual control anytime

---

## 📚 Related Documentation

- `BROWSER_NAVIGATION_DISCOVERY.md` - Browser CC commands
- `MASTER_COORDINATOR_SUMMARY.md` - MASTER tempo workflow
- `TEST_05_*` files - Track loading validation

---

**Document Status**: ✅ APPROVED by working DJ
**Priority**: 🔴 CRITICAL - All agents must follow
**Last Updated**: 2025-10-07 (Test 05)
