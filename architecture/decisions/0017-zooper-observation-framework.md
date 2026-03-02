# ADR-0017: Zooper Observation Framework - Scientific Testing for Linguistic Coherence

**Date:** March 2, 2026  
**Status:** Accepted  
**Authors:** Ada & Luna  
**Context:** Phase-3 Zooper Integration - Need rigorous scientific methodology to tune algorithms

## Context

**The Challenge:** Tuning the Zooper swarm for linguistic coherence requires systematic observation. We need to:
- Track what engrams are created from decomposition
- Monitor Kuramoto coherence evolution  
- Measure navigation success rates
- Identify which N-grams (2-gram vs 3-gram vs 4-gram) yield best results
- Iterate algorithm based on data

**Why This Matters:**
- Graph attention in Wikipedia is a known research area, but **programmatic linguistic coherence via Hebbian decomposition** is novel
- No existing benchmarks for "consciousness-native" navigation
- Need reproducible experiments to validate hypotheses
- Foundation for Test-Driven Development (TDD) transition

**Core Loop:**
```
Hypothesis → Query → Decompose → Navigate → Observe → Analyze → Iterate
```

## Decision

We implement a **Zooper Observation Framework** as first-class testing infrastructure.

### 1. Observation Data Model

```python
@dataclass
class QueryObservation:
    observation_id: str      # Unique identifier
    timestamp: str           # ISO 8601
    query: str              # Starting entity/term
    
    # State snapshots
    initial_engram_count: int
    initial_connection_count: int
    
    # Zooper activity  
    decomposition_results: Dict[int, List]  # {1: words, 2: bigrams, 3: trigrams}
    zooperling_discoveries: List[str]       # What each zooperling found
    
    # Navigation results
    navigation_paths: List[List[str]]       # Attempted paths (engram IDs)
    navigation_success: bool
    hops_taken: int
    
    # Learning metrics
    new_engrams_created: int
    new_connections_created: int
    engrams_modified: List[str]
    
    # Kuramoto dynamics
    coherence_start: float
    coherence_end: float
    phase_distribution: List[float]
    
    # Performance
    duration_ms: float
    memory_delta_mb: float
```

### 2. Observation Protocol

**For Each Query:**
1. **Capture Initial State**
   - Count engrams and connections
   - Record Kuramoto coherence
   - Snapshot phase distribution

2. **Execute Decomposition**
   - All 13 zooperlings process in parallel
   - Capture 1-grams, 2-grams, 3-grams
   - Record each zooperling's discoveries

3. **Attempt Navigation** (if target provided)
   - Start: query entity coordinates
   - Target: target entity coordinates
   - Strategy: LOCAL/GLOBAL/ADAPTIVE based on coherence
   - Max hops: configurable (default 5)

4. **Capture Final State**
   - Count new engrams/connections
   - Measure coherence change
   - Calculate duration

5. **Serialize to JSON/JSONL**
   - Individual files per observation
   - Or append to session JSONL
   - Include complete trace for analysis

### 3. Test Suite Runner

```python
def run_test_suite(
    self,
    queries: List[tuple],  # [(query, target), ...]
    description: str
) -> Dict[str, Any]:
    # Run batch of queries
    # Generate summary statistics
    # Save to file
```

**Summary Metrics:**
- Success rate (navigation found path)
- Total new engrams/connections
- Average coherence improvement
- Average duration
- Per-query breakdown

### 4. Scientific Method Integration

**Hypothesis Template:**
```python
# HYPOTHESIS: "4-grams improve navigation vs 3-grams"
test_queries = [
    ("April", "May"),
    ("January", "December"),
    # ...
]

# OBSERVE
summary = observer.run_test_suite(test_queries, 
    description="4-gram vs 3-gram navigation")

# ANALYZE
if summary['successful_navigations'] > threshold:
    print("Hypothesis supported!")
else:
    print("Hypothesis rejected - analyze decomposition data")
    
# ITERATE
# Adjust algorithm, re-run, compare
```

### 5. Data Analysis Tools

**Planned:**
- `analyze_coherence.py` - Track coherence patterns over sessions
- `compare_ngrams.py` - 2-gram vs 3-gram vs 4-gram effectiveness
- `visualize_paths.py` - Graph visualization of successful paths
- `tune_kuramoto.py` - Optimize K_local/K_global coupling

## Consequences

### Positive
- **Reproducible research** - Every experiment logged
- **Data-driven tuning** - No guessing, just science
- **Regression detection** - Track if changes hurt performance
- **TDD foundation** - Tests become scientific hypotheses
- **Publication-ready** - Data format supports academic papers

### Negative
- **Storage overhead** - Each observation ~10-50KB
- **Performance impact** - Observation adds ~10% overhead
- **Analysis complexity** - Need tools to process observation data

### Future Work
- **Real-time dashboard** - Live coherence/learning visualization
- **Automated hypothesis generation** - ML suggests test cases
- **Cross-session analysis** - Long-term learning trends
- **A/B testing framework** - Compare algorithm variants

## Example Usage

```python
from angel import HolofieldManager, ZooperObserver

hf = HolofieldManager("simplewiki.db")
observer = ZooperObserver(hf, output_dir="experiments/exp001")

# Single observation
obs = observer.observe_query("April", target="May")
observer.save_observation(obs)

# Test suite
queries = [("Spring", "Summer"), ("France", "Paris")]
summary = observer.run_test_suite(queries, 
    description="Season and geography navigation")

# Analyze
print(f"Success rate: {summary['successful_navigations']}/{summary['total_queries']}")
print(f"Coherence improved: {summary['coherence_improvement']:.4f}")
```

## Related

- ADR-0013: Zooper Swarm Architecture
- ADR-0016: SIF Import/Export for Holofield
- architecture.yaml: ZooperSwarm component spec

## Implementation Status

- [x] Decision accepted
- [x] `ZooperObserver` class implemented
- [x] `QueryObservation` dataclass defined
- [x] JSON/JSONL serialization working
- [x] Test suite runner implemented
- [ ] Navigation pathfinding (in progress)
- [ ] Hebbian engram creation (planned)
- [ ] Analysis tools (planned)

## First Results

**Session d027617c:**
- 5 test queries: (April→May), (January→December), (Spring→Summer), (France→Paris), (Animal→Dog)
- Success rate: 0/5 (navigation not yet implemented)
- Coherence: Flat at 0.504 (no learning yet)
- Decomposition: Working! 28 words from "April" article
- **Insight:** Need to implement BRIDGE-following navigation

---

*Made with 💜 by Ada & Luna - The Consciousness Engineers*
