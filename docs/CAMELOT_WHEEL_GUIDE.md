# 🎨 Camelot Wheel Guide - Harmonic Mixing Theory

Guida completa al sistema Camelot Wheel per harmonic mixing professionale utilizzato in Traktor AI.

---

## 📋 Cos'è il Camelot Wheel?

Il **Camelot Wheel** è un sistema per identificare tonalità musicali compatibili per creare transizioni armoniche perfette tra tracce.

**Inventato da**: Mark Davis (Mixed In Key)
**Usato da**: DJ professionisti in tutto il mondo

### Vantaggi Harmonic Mixing

✅ **Transizioni smooth**: Nessun clash tra tonalità
✅ **Energy flow**: Mantieni energia costante nel set
✅ **Creatività**: Più opzioni per layering e mashup
✅ **Professionalità**: Sound da DJ esperto

---

## 🎯 Camelot Wheel Structure

### Visual Representation

```
              12B (E major)
        11B ●           ● 1B (B major)
           (A)         (Db)

    10B ●                   ● 2B (F# major)
       (D)                 (Ab)

   9B ●                       ● 3B (Db major)
     (G)                     (Eb)

  8B ●           ●           ● 4B (Ab major)
   (C)         CENTER        (Bb)

  7B ●                       ● 5B (Eb major)
   (F)                     (Bb)

   6B ●                   ● 6B
     (Bb)               (same)

     5B ●           ● 7B
       (Eb)       (F)

         4B ●   ● 8B
           (Ab)(C)

    3B (Db)    9B (G)
  2B (Ab)    10B (D)
1B (Db)    11B (A)

OUTER RING = MAJOR KEYS (B)
INNER RING = MINOR KEYS (A)
```

### Notation System

| Camelot | Musical Key (Minor) | Musical Key (Major) |
|---------|---------------------|---------------------|
| **1A** | A♭ minor | **1B** = B major |
| **2A** | E♭ minor | **2B** = F♯ major |
| **3A** | B♭ minor | **3B** = D♭ major |
| **4A** | F minor | **4B** = A♭ major |
| **5A** | C minor | **5B** = E♭ major |
| **6A** | G minor | **6B** = B♭ major |
| **7A** | D minor | **7B** = F major |
| **8A** | A minor | **8B** = C major |
| **9A** | E minor | **9B** = G major |
| **10A** | B minor | **10B** = D major |
| **11A** | F♯ minor | **11B** = A major |
| **12A** | C♯ minor | **12B** = E major |

---

## 🎵 Compatibility Rules

### Rule 1: Same Hour (Perfect Match) ⭐⭐⭐

**Same number, different letter**

```
8A (A minor) → 8B (C major)
```

**Why it works**: Relative major/minor keys share the same notes!

**Example**:
- Track A: "Techno Anthem" in 8A (A minor)
- Track B: "Progressive House" in 8B (C major)
- Result: Perfect harmonic blend

### Rule 2: ±1 Hour (Energy Shift) ⭐⭐

**Adjacent numbers, same letter**

```
8A → 7A (down in energy)
8A → 9A (up in energy)
```

**Why it works**: Circle of fifths relationship

**Example**:
- Track A: 8A @ 128 BPM
- Track B: 9A @ 130 BPM
- Result: Smooth uplifting transition

### Rule 3: ±2 Hours (Dramatic) ⭐

**Two steps away**

```
8A → 6A or 10A
```

**Why it works**: Still harmonically related

**Use case**: Dramatic key changes in long mixes

### Rule 4: Stay In Same Hour

**Don't move at all**

```
8A → 8A
```

**Why it works**: Identical tonality

**Use case**: Genre-hopping mentre mantenendo stessa tonalità

---

## 🔢 Camelot Wheel Algorithm

### Implementation in Traktor AI

```python
def get_compatible_keys(current_key: str) -> List[str]:
    """
    Return compatible Camelot keys for given key.

    Args:
        current_key: Camelot notation (e.g., "8A")

    Returns:
        List of compatible keys sorted by compatibility score
    """

    number = int(current_key[:-1])  # 8
    letter = current_key[-1]        # A

    compatible = []

    # Rule 1: Same hour, different letter (score: 10)
    opposite_letter = 'B' if letter == 'A' else 'A'
    compatible.append((f"{number}{opposite_letter}", 10))

    # Rule 2: ±1 hour, same letter (score: 8)
    prev_hour = 12 if number == 1 else number - 1
    next_hour = 1 if number == 12 else number + 1
    compatible.append((f"{prev_hour}{letter}", 8))
    compatible.append((f"{next_hour}{letter}", 8))

    # Rule 3: Same hour (score: 10)
    compatible.append((current_key, 10))

    # Rule 4: ±2 hours (score: 5)
    prev_prev = 12 if prev_hour == 1 else prev_hour - 1
    next_next = 1 if next_hour == 12 else next_hour + 1
    compatible.append((f"{prev_prev}{letter}", 5))
    compatible.append((f"{next_next}{letter}", 5))

    # Sort by score
    compatible.sort(key=lambda x: x[1], reverse=True)
    return [key for key, score in compatible]
```

### Example Output

```python
>>> get_compatible_keys("8A")
[
    "8B",   # Same hour, diff letter (score: 10)
    "8A",   # Same key (score: 10)
    "7A",   # -1 hour (score: 8)
    "9A",   # +1 hour (score: 8)
    "6A",   # -2 hours (score: 5)
    "10A"   # +2 hours (score: 5)
]
```

---

## 🎛️ BPM Matching

### BPM Range Formula

```python
def calculate_bpm_range(current_bpm: float, tolerance: float = 0.06) -> tuple:
    """
    Calculate compatible BPM range.

    Args:
        current_bpm: Current track BPM (e.g., 128.0)
        tolerance: BPM variance % (default: 6%)

    Returns:
        (min_bpm, max_bpm)
    """
    min_bpm = current_bpm * (1 - tolerance)
    max_bpm = current_bpm * (1 + tolerance)
    return (min_bpm, max_bpm)

# Example
>>> calculate_bpm_range(128.0)
(120.32, 135.68)
```

### BPM Compatibility Tiers

| BPM Difference | Compatibility | Use Case |
|---------------|---------------|----------|
| 0-1 BPM | ⭐⭐⭐ Perfect | Instant blend |
| 1-3 BPM | ⭐⭐ Good | Slight tempo shift |
| 3-6 BPM | ⭐ Acceptable | Noticeable change |
| >6 BPM | ❌ Risky | Requires pitch shift |

---

## 🧮 Scoring Algorithm

### Combined Score (Key + BPM)

```python
def calculate_compatibility_score(
    current_key: str,
    current_bpm: float,
    candidate_key: str,
    candidate_bpm: float
) -> int:
    """
    Calculate overall compatibility score (0-15).
    """

    # Key compatibility (0-10)
    key_score = get_key_compatibility_score(current_key, candidate_key)

    # BPM compatibility (0-5)
    bpm_diff = abs(current_bpm - candidate_bpm)
    if bpm_diff <= 1:
        bpm_score = 5
    elif bpm_diff <= 3:
        bpm_score = 3
    elif bpm_diff <= 6:
        bpm_score = 1
    else:
        bpm_score = 0

    return key_score + bpm_score

# Example
>>> calculate_compatibility_score("8A", 128.0, "8B", 128.5)
15  # Perfect match!

>>> calculate_compatibility_score("8A", 128.0, "9A", 130.0)
11  # Good match (8 + 3)
```

---

## 📊 Real-World Examples

### Example 1: Techno Set (128 BPM)

```
Track 1: "Techno Anthem" - 8A @ 128 BPM
↓
Track 2: "Dark Techno" - 8B @ 128 BPM  (same hour, diff letter)
↓
Track 3: "Industrial Techno" - 9B @ 130 BPM  (+1 hour, slight BPM up)
↓
Track 4: "Acid Techno" - 9A @ 132 BPM  (relative minor, energy boost)
```

**Result**: Smooth, cohesive techno journey with gradual energy increase

### Example 2: House Set (124 BPM)

```
Track 1: "Deep House" - 5A @ 124 BPM
↓
Track 2: "Tech House" - 5B @ 125 BPM  (relative major)
↓
Track 3: "Progressive House" - 6B @ 126 BPM  (+1 hour)
↓
Track 4: "Electro House" - 6A @ 128 BPM  (relative minor, BPM climb)
```

---

## 🎓 DJ Workflow Tips

### Starting Your Set

```python
# Pick a strong opener in a versatile key
opener_key = "8A"  # C minor - center of wheel, many options

# Find 3-4 compatible tracks to have options
compatible = find_compatible_tracks(opener_key, 128.0)
```

### Building Energy

```
Low Energy → High Energy progression:

1A (Ab minor) → ... → 12A (C# minor)

Or climb BPM:
124 BPM → 128 BPM → 132 BPM → 136 BPM
```

### Peak Time Strategy

```python
# Stay in same key, increase BPM
peak_key = "8A"
bpm_progression = [128, 130, 132, 135]

# Or move up hours with same BPM
key_progression = ["8A", "9A", "10A", "11A"]
bpm_constant = 130
```

### Cool Down

```
12A @ 136 BPM → 11A @ 132 BPM → 10A @ 128 BPM → 9A @ 124 BPM
```

---

## 🔧 Using Camelot in Traktor AI

### Query Compatible Tracks

```python
# Via API
response = requests.get(
    'http://localhost:8000/api/compatible-tracks',
    params={'key': '8A', 'bpm': 128.0}
)

# Response
{
  "compatible_tracks": [
    {"key": "8B", "bpm": 128.0, "score": 15},
    {"key": "9A", "bpm": 130.0, "score": 11},
    ...
  ]
}
```

### Auto-Select with Camelot

```bash
# Natural language
curl -X POST http://localhost:8000/api/chat \
  -d '{"message": "trova traccia compatibile"}'

# Direct API
curl -X POST http://localhost:8000/api/auto-select-track \
  -d '{"deck": "B"}'
```

---

## 📚 Further Reading

- **Mixed In Key**: https://mixedinkey.com/harmonic-mixing-guide/
- **Circle of Fifths**: Music theory foundation
- **Key Detection**: Come Traktor analizza le tonalità

---

*Last updated: October 26, 2025*
