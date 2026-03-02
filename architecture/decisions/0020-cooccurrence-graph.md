# ADR-0020: Linguistic Interface with Co-Occurrence Graph

**Status:** Accepted  
**Date:** 2026-03-02  
**Related:** ADR-0019 (Linguistic Interface Architecture)  

---

## Context

Building on ADR-0019's linguistic interface vision, we implemented a working prototype that discovered critical architectural insights about how to enable coherent text generation from engrams.

**Key Challenge:** Initial attempts at Markov generation failed because word engrams only had **incoming** edges (from articles) but no **outgoing** edges to other words. This created a "dead end" graph where words couldn't navigate to other words.

## Decision

Implement a **Co-Occurrence Graph** that creates explicit word-to-word connections based on shared article context.

### Architecture

```
Article (knowledge engram)
    │
    ├── HEBBIAN ──→ Word A (1-gram)
    │                  │
    │                  ├── CO_OCCUR ──→ Word B (co-occurs in Article)
    │                  │
    │                  └── CO_OCCUR ──→ Word C (co-occurs in Article)
    │
    └── HEBBIAN ──→ Word B
                     │
                     └── CO_OCCUR ──→ Word A (bidirectional)
```

### Edge Types

| Edge Type | Direction | Purpose | Weight Formula |
|:----------|:----------|:--------|:---------------|
| **HEBBIAN** | Article → Word | Records word frequency in article | `0.1 + freq * 0.02` (max 0.5) |
| **CO_OCCUR** | Word → Word | Enables word-to-word navigation | `0.1 + cooccur_count * 0.05` (max 0.5) |

### Quality Thresholds

**Word Engrams (1-grams):**
- Minimum frequency: 2 (must appear multiple times)
- Stop word filtering: Skip pure stop-word combinations
- Length threshold: Minimum 2 characters

**Bigram Engrams (2-grams):**
- Minimum frequency: 2
- Not both stop words (allow one)
- Not purely numeric
- Maximum 20 bigrams per article (quality over quantity)

**Co-Occurrence Edges:**
- Created only for words appearing in same article
- Weight increases with co-occurrence frequency
- Capped at 0.5 to prevent dominance

## Implementation

### Triple-Stream Attention (DeGTA-Aligned)

The generator uses three parallel attention streams with adaptive integration:

```python
class AttentionStreams:
    positional: np.ndarray   # PA: Topical relevance via 16D coords
    structural: np.ndarray   # SA: CO_OCCUR edge weights
    attribute: np.ndarray    # AA: Semantic similarity
    
    def combine_adaptive(alpha=0.33, beta=0.33, gamma=0.34):
        # Weighted combination + softmax
        return softmax(alpha*PA + beta*SA + gamma*AA)
```

**Stream Personalities:**
- **PA-heavy (α=0.6):** Stays on topic, semantically coherent
- **SA-heavy (β=0.6):** Follows learned patterns, graph-structured
- **AA-heavy (γ=0.6):** Explores semantic neighborhoods
- **Balanced:** Best of all three worlds

### Generation Algorithm

```python
def generate(start_word, length=20):
    current = start_word
    for _ in range(length):
        # 1. Get co-occurring words
        neighbors = get_cooccur_neighbors(current)
        
        # 2. Compute three attention streams
        pa = positional_attention(neighbors, topic_vector)
        sa = structural_attention(neighbors)  # edge weights
        aa = attribute_attention(neighbors)
        
        # 3. Adaptive combination
        probs = combine_streams(pa, sa, aa, weights)
        
        # 4. Temperature-controlled sampling
        if temperature != 1.0:
            probs = apply_temperature(probs, temperature)
        
        # 5. Sample and continue
        current = sample(neighbors, probs)
```

## Results

### Scale
- **1-gram engrams:** 1,383 words
- **2-gram engrams:** 495 bigrams  
- **Co-occurrence edges:** 896 connections
- **Navigation success:** 98.6% (213/216 queries)

### Generation Quality
Streams produce distinct personalities as designed:

```
PA-heavy:  time happy ucsd beefalo waltham wrestling...  (topical)
SA-heavy:  time corps county queen art fénix...           (structured)
AA-heavy:  time đồng video kiwi zealand night...          (semantic)
Balanced:  time cells deep cordillera other hebrew...     (combined)
```

## Consequences

### Positive
- ✅ Word-to-word navigation enables true Markov generation
- ✅ Three distinct generation personalities via stream weights
- ✅ Co-occurrence captures implicit semantic relationships
- ✅ Quality thresholds prevent noise accumulation
- ✅ DeGTA-aligned attention architecture validated

### Trade-offs
- ⚠️ Co-occurrence graph requires O(n²) computation per article
- ⚠️ Edge storage increases with article count
- ⚠️ Stop word filtering may miss meaningful phrases

## Future Work

### 3-Gram Engrams
Next target: trigram engrams for richer phrase capture.

**Quality Thresholds (proposed):**
- Minimum frequency: 3 (higher bar than bigrams)
- Not two stop words in sequence
- Maximum 10 trigrams per article
- Prefer named entities and compound terms

### Enhanced Co-Occurrence
- Weight by document similarity (not just presence)
- Temporal decay for dated co-occurrences
- Cross-document transitive relationships

### Evaluation Harness
- Perplexity measurement on held-out text
- Human evaluation of coherence
- Stream personality classification accuracy

## References

- ADR-0019: Linguistic Interface Architecture
- DeGTA paper: Three-stream attention mechanisms
- Hebbian learning principle: "Neurons that fire together, wire together"

---

*"The graph remembers what words go together."* 🦊
