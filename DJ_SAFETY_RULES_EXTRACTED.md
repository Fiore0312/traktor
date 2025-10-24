# DJ Safety Rules - Extracted from DJ_WORKFLOW_RULES.md

**Date**: 2025-10-23
**Source**: DJ_WORKFLOW_RULES.md (33 years DJ experience)
**Purpose**: Safety layer implementation for autonomous DJ system

---

## 📋 PRE-LOAD CHECKS

### Rule 1: Check Deck Playing State
**BEFORE loading ANY track**:
- ✅ Verify if ANY deck is currently playing
- ✅ Identify which deck is MASTER (if any)
- ✅ Determine target deck for new track

**Implementation**:
```python
# Cannot read Traktor state via MIDI
# Must use VISION-based verification
# OR maintain internal state tracking
```

### Rule 2: Volume Safety Check
**Target deck MUST have volume at ZERO before load**:
- ✅ Set volume fader to 0% on deck being loaded
- ✅ Prevents audio spikes from previous track
- ✅ Prevents accidental loud playback

**CC Mapping**:
- Deck A Volume: CC 65
- Deck B Volume: CC 60
- Deck C Volume: CC 61
- Deck D Volume: CC 62

### Rule 3: Crossfader Position Check
**Crossfader must be AWAY from target deck**:
- Loading to Deck A → Crossfader should be RIGHT (away from A)
- Loading to Deck B → Crossfader should be LEFT (away from B)
- **OR** use volume fader at 0% as safety

**CC Mapping**:
- Crossfader: CC 8 (0=Full Left/A, 64=Center, 127=Full Right/B)

### Rule 4: Opposite Deck Protection
**If opposite deck is playing**:
- ✅ Ensure it continues undisturbed
- ✅ Do NOT touch its volume/EQ/crossfader
- ✅ Focus safety on TARGET deck only

---

## 🎚️ POST-LOAD ACTIONS

### Rule 5: Reset Deck Controls to Neutral
**IMMEDIATELY after loading track**:
1. ✅ **Volume**: Set to 0% (prevent audio leak)
2. ✅ **Gain**: Set to CENTER (64 = 12 o'clock, neutral)
3. ✅ **EQ High**: Set to CENTER (64 = neutral, no boost/cut)
4. ✅ **EQ Mid**: Set to CENTER (64 = neutral)
5. ✅ **EQ Low**: Set to CENTER (64 = neutral)
6. ✅ **Filter**: Set to CENTER if available (bypass/neutral)

**Why?**:
- Previous track may have had EQ adjustments
- Gain may have been boosted/cut
- Starting neutral = predictable, professional sound

**CC Mapping**:

| Control | Deck A | Deck B | Deck C | Deck D | Neutral Value |
|---------|--------|--------|--------|--------|---------------|
| Volume  | CC 65  | CC 60  | CC 61  | CC 62  | 0 (silent)    |
| Gain    | N/A    | N/A    | N/A    | N/A    | 64 (center)   |
| EQ High | CC 34  | CC 50  | CC 84  | CC 66  | 64 (center)   |
| EQ Mid  | CC 35  | CC 51  | CC 85  | CC 67  | 64 (center)   |
| EQ Low  | CC 36  | CC 52  | CC 86  | CC 68  | 64 (center)   |

**NOTE**: Gain CC not in current mapping - may need TSI verification

### Rule 6: Enable Cue for Preview
**Optional but recommended**:
- ✅ Activate headphone cue on loaded deck
- ✅ Allows DJ to preview track before playing to audience
- ✅ Verify beatmatching and EQ before going live

**Implementation**: Cue CC not in current mapping - vision-based or manual

---

## 🔊 MIXER SAFETY DEFAULTS

### Safe Starting Values

| Parameter | Value | MIDI CC Value | Purpose |
|-----------|-------|---------------|---------|
| **Volume Fader** | 0% | 0 | No audio leak |
| **Gain** | 12 o'clock | 64 | Neutral, no clipping |
| **EQ High** | 12 o'clock | 64 | Flat frequency response |
| **EQ Mid** | 12 o'clock | 64 | Flat frequency response |
| **EQ Low** | 12 o'clock | 64 | Flat frequency response |
| **Filter** | Bypass | 64 | No effect applied |
| **Crossfader** | Away from deck | 0 or 127 | Deck inaudible |

### Master Output Safety
- **Master Volume**: Typically 75-85% (CC 75)
- **Avoid**: Master > 90% (risk of clipping/distortion)
- **Headroom**: Keep ~15-20% headroom for peaks

---

## ⚠️ CRITICAL SAFETY RULES

### Rule 7: Volume Fader BEFORE Play
**ALWAYS set volume BEFORE pressing play**:
```
WRONG:
  Load → Play → Set Volume (audio spike!)

CORRECT:
  Load → Set Volume to 0 → Reset EQ/Gain → THEN Play
```

### Rule 8: Never Interrupt Playing Deck
**When another deck is playing**:
- ❌ Do NOT touch its volume fader
- ❌ Do NOT touch its EQ settings
- ❌ Do NOT move crossfader away from it
- ✅ Only modify the INCOMING (silent) deck

### Rule 9: Crossfader OR Volume Method
**Two valid approaches** (pick one):

**Method A - Crossfader Control**:
- Keep volume faders at 85%
- Use crossfader to control what audience hears
- Move crossfader away from target deck before load

**Method B - Volume Fader Control**:
- Keep crossfader at center
- Lower volume fader to 0% on target deck
- Raise volume when ready to mix

**Method C - Combined (SAFEST)**:
- Lower volume fader to 0% AND
- Move crossfader away from deck
- Double protection against audio leaks

### Rule 10: MASTER/SYNC Logic (AUTO Mode)
**First track** (empty session):
- ✅ Set as MASTER (manual, CC 33/37/38/39 depending on deck)
- ❌ Do NOT enable SYNC (nothing to sync to)
- ✅ Set volume HIGH (85%)

**Second+ track** (deck already playing):
- ❌ Do NOT set as MASTER (AUTO mode handles it)
- ✅ Enable SYNC (CC 69/42/59/63 depending on deck)
- ✅ Start volume LOW (0-20%)
- ✅ During transition: volume up → AUTO transfers MASTER

---

## 🎯 PRE-PLAYBACK CHECKLIST

**BEFORE pressing PLAY on ANY deck**:

### If FIRST track (empty session):
- [ ] Check: No other deck is playing ✅
- [ ] Set: Volume fader HIGH (85%) or ready position
- [ ] Set: Crossfader to deck's side (A=Left, B=Right)
- [ ] Set: MASTER ON
- [ ] Set: SYNC OFF
- [ ] Set: EQ neutral (all at 64)
- [ ] **THEN**: Press PLAY

### If SECOND+ track (deck already playing):
- [ ] Check: Another deck IS playing ✅
- [ ] Set: Volume fader to 0%
- [ ] Set: Crossfader AWAY from new deck
- [ ] Set: SYNC ON
- [ ] Set: MASTER OFF (let AUTO handle it)
- [ ] Set: EQ neutral (all at 64)
- [ ] Set: Gain neutral (64)
- [ ] **THEN**: Press PLAY (deck plays silently)
- [ ] **THEN**: Gradually fade in when ready

---

## 🛡️ EMERGENCY SAFETY ACTIONS

### If Audio Spike Detected:
1. **Immediately**: Set deck volume to 0 (CC 65/60/61/62)
2. **Then**: Move crossfader away
3. **Then**: Investigate cause (wrong deck loaded, EQ misconfigured, etc.)

### If Clipping/Distortion Heard:
1. **Check**: Master volume not > 90%
2. **Check**: Deck gain not boosted (should be 64)
3. **Check**: EQ not excessively boosted
4. **Action**: Reduce gain or lower volume slightly

### If MASTER Tempo Chaos:
1. **Verify**: Only ONE deck should be MASTER at a time
2. **Check**: SYNC is enabled on non-MASTER deck
3. **Action**: Manually set correct MASTER if AUTO fails

---

## 📊 MIXER STATE MATRIX

### Safe States for Each Scenario

| Scenario | Deck A Vol | Deck B Vol | Crossfader | Master | Safe? |
|----------|------------|------------|------------|--------|-------|
| **Load to A (B playing)** | 0% | 85% | RIGHT (127) | B | ✅ |
| **Load to B (A playing)** | 85% | 0% | LEFT (0) | A | ✅ |
| **Both playing (mix)** | 50-85% | 50-85% | CENTER (64) | AUTO | ✅ |
| **Load to A (nothing playing)** | 0→85% | 0% | LEFT (0) | A | ✅ |
| **Load to B (nothing playing)** | 0% | 0→85% | RIGHT (127) | B | ✅ |

### Unsafe States (AVOID!)

| Scenario | Deck A Vol | Deck B Vol | Crossfader | Problem |
|----------|------------|------------|------------|---------|
| Load to A (B playing) | 85% | 85% | CENTER | Audio spike from A! |
| Load to A (B playing) | 50% | 85% | LEFT | B becomes inaudible! |
| Both have MASTER ON | N/A | N/A | N/A | Tempo chaos! |

---

## 🔧 IMPLEMENTATION PRIORITIES

### CRITICAL (Must Implement):
1. ✅ Volume to 0 before load
2. ✅ EQ/Gain reset after load
3. ✅ MASTER/SYNC decision logic
4. ✅ Crossfader positioning OR volume method

### IMPORTANT (Should Implement):
5. ✅ Opposite deck protection
6. ✅ Master volume monitoring
7. ✅ Cue activation for preview

### OPTIONAL (Nice to Have):
8. ⚠️ Vision-based state verification
9. ⚠️ Audio level monitoring
10. ⚠️ Auto-EQ compensation

---

## 📝 NOTES

**Gain Control Missing**:
- Current JSON mapping does NOT include Gain CC numbers
- Gain is CRITICAL for preventing clipping
- Need to verify in TSI or use MIDI Learn

**Filter Control Missing**:
- Filter CC not in current mapping
- Less critical than Gain/EQ
- Can be added later if needed

**Cue Control Missing**:
- Headphone cue CC not mapped
- Important for professional workflow
- Alternative: Manual cue activation by DJ

---

**Last Updated**: 2025-10-23
**Status**: ✅ Ready for implementation
**Source**: DJ_WORKFLOW_RULES.md + traktor_midi_mapping.json
