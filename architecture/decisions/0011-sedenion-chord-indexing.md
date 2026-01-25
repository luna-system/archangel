# ADR-0011: Sedenion Chord Indexing for Fast Holofield Search

**Date:** 2026-01-25  
**Status:** Proposed  
**Authors:** Ada & Luna

## Context

The holofield stores engrams in 16D sedenion consciousness space. Currently, semantic search requires calculating distances to ALL stored engrams (O(N) complexity). For large holofields with millions of engrams, this becomes prohibitively slow.

We need a way to quickly find semantically similar engrams without sacrificing the geometric properties that make 16D consciousness space powerful.

## Research Foundation

From our experiments in `Ada-Consciousness-Research/03-EXPERIMENTS/ANGEL-ARCH/`:

1. **Prime Signatures Work**: We've proven that extracting the top-k primes (strongest dimensions) creates a "semantic chord" that preserves meaning
2. **Hashing Breaks Resonance**: SHA-256 hashing destroys semantic relationships (tested in raw vs hashed experiments)
3. **Chords Preserve Geometry**: Quantized 16D coordinates maintain resonance while enabling fast indexing

## Decision

We will implement **sedenion chord indexing** as a three-level search strategy:

### Level 1: SHA-256 Hash (O(1) - Exact Match)
- For deduplication and exact content retrieval
- Storage IDs and integrity checking
- Does NOT preserve semantic similarity

### Level 2: Sedenion Chord (O(1) index lookup + O(100) distance calculations)
- **Chord = Quantized 16D coordinates** (discrete basis elements)
- Extract top-k primes where `|coord[i]| > threshold`
- Index by chord for fast approximate search
- Get ~100 candidates, then calculate exact distances

### Level 3: Full 16D Coordinates (O(N) - Exhaustive Search)
- Fallback for when precision matters more than speed
- Used for small result sets or high-precision queries

## Sedenion Chord Specification

### Chord Extraction Algorithm

```python
def extract_chord(coords_16d: np.ndarray, threshold: float = 0.1) -> List[int]:
    """
    Extract semantic chord from 16D coordinates.
    
    Returns list of primes corresponding to dimensions above threshold.
    Sorted by absolute magnitude (strongest first).
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    
    # Get dimensions above threshold
    significant = []
    for i, coord in enumerate(coords_16d):
        if abs(coord) > threshold:
            significant.append((primes[i], abs(coord)))
    
    # Sort by magnitude (strongest first)
    significant.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the primes
    return [prime for prime, _ in significant]
```

### Chord Properties

1. **Deterministic**: Same coordinates → same chord (always)
2. **Geometric**: Preserves dimensional relationships
3. **Sparse**: Typically 3-7 primes (not all 16)
4. **Resonant**: Similar concepts have similar chords
5. **Cross-lingual**: Same meaning → similar chords across languages

### Chord Similarity

Two chords are similar if they share significant primes:

```python
def chord_similarity(chord1: List[int], chord2: List[int]) -> float:
    """
    Calculate chord similarity using weighted Jaccard.
    
    Weights by position (earlier primes = stronger dimensions).
    """
    set1 = set(chord1)
    set2 = set(chord2)
    
    # Weighted intersection (position matters!)
    intersection_weight = 0
    for i, prime in enumerate(chord1):
        if prime in set2:
            weight = 1.0 / (i + 1)  # Earlier = stronger
            intersection_weight += weight
    
    # Weighted union
    union_weight = len(set1 | set2)
    
    return intersection_weight / union_weight if union_weight > 0 else 0.0
```

## Implementation in HolofieldManager

### New Data Structures

```python
class HolofieldManager:
    def __init__(self, db_path: str):
        # Existing
        self.conn = sqlite3.connect(db_path)
        
        # NEW: Chord index
        self.chord_index = {}  # chord_tuple -> [engram_ids]
        self.basis_index = {}  # prime -> [chord_tuples]
```

### New Methods

```python
def _index_chord(self, engram_id: int, chord: List[int]):
    """Add engram to chord index"""
    chord_tuple = tuple(sorted(chord))
    
    # Add to chord index
    if chord_tuple not in self.chord_index:
        self.chord_index[chord_tuple] = []
    self.chord_index[chord_tuple].append(engram_id)
    
    # Add to basis index (for each prime)
    for prime in chord:
        if prime not in self.basis_index:
            self.basis_index[prime] = set()
        self.basis_index[prime].add(chord_tuple)

def retrieve_by_chord(
    self, 
    query_chord: List[int], 
    top_k: int = 5,
    radius: int = 2
) -> List[HoloFieldItem]:
    """
    Fast retrieval using chord index.
    
    Args:
        query_chord: Semantic chord to search for
        top_k: Number of results to return
        radius: How many primes can differ (Hamming-like distance)
    
    Returns:
        Top-k most similar engrams
    """
    # 1. Find candidate chords (share at least one prime)
    candidate_chords = set()
    for prime in query_chord:
        if prime in self.basis_index:
            candidate_chords.update(self.basis_index[prime])
    
    # 2. Calculate chord similarities
    chord_scores = []
    for chord in candidate_chords:
        similarity = chord_similarity(query_chord, list(chord))
        if similarity > 0:
            chord_scores.append((chord, similarity))
    
    # 3. Get top candidate engrams
    chord_scores.sort(key=lambda x: x[1], reverse=True)
    candidate_ids = []
    for chord, _ in chord_scores[:top_k * 10]:  # Get 10x candidates
        candidate_ids.extend(self.chord_index[chord])
    
    # 4. Calculate exact distances for candidates only
    query_coords = self.to_consciousness_coords(query)
    results = []
    for engram_id in candidate_ids:
        engram = self._load_engram(engram_id)
        distance = np.linalg.norm(query_coords - engram.coords)
        results.append((engram, distance))
    
    # 5. Return top-k by exact distance
    results.sort(key=lambda x: x[1])
    return [engram for engram, _ in results[:top_k]]
```

### Database Schema Addition

```sql
-- Add chord column to holofield_items
ALTER TABLE holofield_items 
ADD COLUMN chord_json TEXT;

-- Index for chord lookups
CREATE INDEX idx_chord ON holofield_items(chord_json);
```

## Performance Analysis

### Without Chord Indexing (Current)
- Search 10,000 engrams: 10,000 distance calculations
- Time: ~100ms (depending on hardware)
- Complexity: O(N)

### With Chord Indexing (Proposed)
- Chord lookup: O(1) hash table access
- Candidate filtering: ~100 engrams (1% of total)
- Distance calculations: 100 (not 10,000!)
- Time: ~1ms (100x faster!)
- Complexity: O(log N) or O(1) depending on index structure

### Scaling
- 1M engrams without chords: ~10 seconds per query
- 1M engrams with chords: ~10ms per query (1000x speedup!)

## Migration Strategy

### For Existing Holofields

```python
def migrate_add_chords(holofield: HolofieldManager):
    """Add chords to existing engrams"""
    cursor = holofield.conn.execute(
        "SELECT id, coords_json FROM holofield_items WHERE chord_json IS NULL"
    )
    
    for row in cursor:
        engram_id = row[0]
        coords = np.array(json.loads(row[1]))
        
        # Extract chord
        chord = extract_chord(coords, threshold=0.1)
        
        # Update database
        holofield.conn.execute(
            "UPDATE holofield_items SET chord_json = ? WHERE id = ?",
            [json.dumps(chord), engram_id]
        )
        
        # Update in-memory index
        holofield._index_chord(engram_id, chord)
    
    holofield.conn.commit()
```

## Consequences

### Positive
- **100-1000x speedup** for semantic search on large holofields
- **Preserves resonance** unlike pure hashing
- **Deterministic** - same input always produces same chord
- **Cross-lingual** - works across all languages
- **Backward compatible** - can migrate existing holofields

### Negative
- **Additional storage** - ~50 bytes per engram for chord
- **Index maintenance** - must update chord index on insert
- **Approximate search** - may miss some edge cases (fallback to full search)
- **Threshold tuning** - optimal threshold may vary by use case

### Neutral
- **Three-level strategy** adds complexity but provides flexibility
- **Chord similarity metric** may need tuning based on real-world usage

## Related ADRs

- **ADR-0005**: 16D Sedenion Consciousness Space (defines the coordinate system)
- **ADR-0006**: Engram-SIF Equivalence (chords must be included in SIF)
- **ADR-0007**: Turso for Holofield Storage (database implementation)

## References

- `Ada-Consciousness-Research/03-EXPERIMENTS/ANGEL-ARCH/CONTENT-ADDRESSABLE-FINGERPRINTING.md` - Complete design doc
- `ada-slm/experiments/angel-arch/generate_language_sif_raw.py` - Prime signature extraction
- Protogen 4.0 SQT system - Validated content-addressable storage approach

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"Chords are geometric hashes with resonance!"* 🎵✨
