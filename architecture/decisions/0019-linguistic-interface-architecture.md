# ADR-0019: Linguistic Interface Architecture - Triple-Stream Markov Generation

**Date:** March 2, 2026  
**Status:** Draft  
**Authors:** Ada & Luna  
**Context:** Post-Zooper RC1 - Enabling Linguistic Communication via Graph Traversal

## Context

With **Zooper RC1** operational (ADR-0013), **461 language engrams** created from navigation (98.8% success rate), and **DeGTA research** (GNN-Attention-Synthesis.md) validating our **three-stream decoupled attention** approach, we now have the foundation for **linguistic I/O**.

### What We Have

- ✅ **Language engrams** - words as first-class engrams with HEBBIAN edges
- ✅ **Navigation infrastructure** - LOCAL/GLOBAL/ADAPTIVE modes
- ✅ **Three attention streams** - Positional (16D), Structural (wikilinks), Attribute (words)
- ✅ **DeGTA validation** - independent attention streams prevent multi-view chaos

### What We're Building

**Linguistic Interface** - bidirectional text processing that:
1. **Input:** Parse text → navigate engram graph → semantic understanding
2. **Output:** Markov-walk graph → generate coherent text sequences
3. **Use triple-stream attention** per DeGTA insights
4. **Integrate with existing Zooper navigation** seamlessly

## Decision

We implement a **DeGTA-inspired triple-stream linguistic architecture**:

### 1. Input Stream: Text → Semantic Navigation

**Process:**
```python
def parse_input(text: str) -> SemanticPath:
    """
    Convert text to engram navigation path.
    """
    # 1. Decompose text to words
    words = decompose(text)
    
    # 2. Find word engrams (or create if new)
    word_engrams = [find_or_create_word_engram(w) for w in words]
    
    # 3. Navigate graph to find semantic centroid
    semantic_coords = compute_centroid(word_engrams)
    
    # 4. Return navigable path
    return SemanticPath(word_engrams, semantic_coords)
```

**Key insight:** Text becomes **traversal instructions** through engram space.

### 2. Output Stream: Markov-Walk Text Generation

**Process:**
```python
def generate_text(
    start_word: str,
    length: int = 20,
    topic_coords: Optional[np.ndarray] = None
) -> str:
    """
    Generate text via DeGTA-style triple-stream attention.
    """
    current = start_word
    text = [current]
    
    for _ in range(length):
        # Get neighbors via HEBBIAN edges
        neighbors = get_hebbian_neighbors(current)
        
        # TRIPLE-STREAM ATTENTION (DeGTA-style!)
        # Stream 1: Positional (topical relevance)
        if topic_coords is not None:
            pos_weights = [
                semantic_similarity(n.coords, topic_coords)
                for n in neighbors
            ]
        else:
            pos_weights = [1.0] * len(neighbors)
        
        # Stream 2: Structural (grammatical patterns)
        struct_weights = [
            edge.weight * grammatical_compatibility(current, n)
            for n, edge in neighbors
        ]
        
        # Stream 3: Attribute (semantic coherence)
        attr_weights = [
            shared_context_score(current, n)
            for n in neighbors
        ]
        
        # ADAPTIVE INTEGRATION (learned gating)
        final_weights = adaptive_combine(
            pos_weights, struct_weights, attr_weights
        )
        
        # Sample next word
        next_word = weighted_choice(neighbors, final_weights)
        text.append(next_word.content)
        current = next_word
    
    return " ".join(text)
```

**DeGTA alignment:**
- **Positional Attention** = topical relevance via 16D coordinates
- **Structural Attention** = grammatical/sequential patterns
- **Attribute Attention** = semantic word relationships

### 3. Interface Abstraction Layer

**Core Interface:**
```python
class LinguisticInterface:
    """
    High-level language I/O for Archangel consciousness.
    """
    
    def __init__(self, swarm: ZooperSwarm):
        self.swarm = swarm
        self.input_processor = InputProcessor(swarm)
        self.output_generator = MarkovGenerator(swarm)
    
    def read(self, text: str) -> SemanticContext:
        """
        Read text → return semantic context (navigable engram path).
        """
        return self.input_processor.parse(text)
    
    def write(
        self,
        context: SemanticContext,
        length: int = 20,
        style: Optional[str] = None
    ) -> str:
        """
        Generate text from semantic context.
        """
        return self.output_generator.generate(
            start=context.anchor_word,
            length=length,
            topic_coords=context.centroid,
            style=style
        )
    
    def converse(self, input_text: str) -> str:
        """
        Full I/O cycle: read → understand → respond.
        """
        context = self.read(input_text)
        # Could modify context based on reasoning
        return self.write(context, length=50)
```

## Implementation Phases

### Phase 1: Basic Markov Generation (Now)
- Simple weighted random walk on word engrams
- Single-stream (structural only)
- No topical guidance

### Phase 2: Triple-Stream Attention (Next)
- Implement all three DeGTA streams
- Adaptive integration via learned weights
- Topical guidance via 16D coordinates

### Phase 3: Contextual Response (Future)
- Full input → process → output cycle
- Maintain conversation state
- Style adaptation

## Technical Considerations

### 1. Engram Lookup Performance

**Challenge:** Word engram lookup must be fast for real-time generation.

**Solution:** 
- Index word engrams by content (already in schema)
- Cache frequent words in memory
- Use `LIKE` queries for partial matches

### 2. Edge Weight Dynamics

**Challenge:** HEBBIAN edge weights change as system learns.

**Solution:**
- Edge weights are dynamic (stored in DB)
- Query fresh weights each generation
- Optional: cache with TTL for performance

### 3. Triple-Stream Integration

**Challenge:** Combining three attention streams without "multi-view chaos."

**Solution:**
- **Explicit separation** (per DeGTA)
- **Learned gating** for adaptive integration
- **Independent computation** before combination

### 4. Topical Coherence

**Challenge:** Generated text should stay on topic.

**Solution:**
- Use 16D semantic coordinates as "topic vector"
- Positional attention weights by coordinate similarity
- Biases generation toward semantically related words

## Consequences

### Positive
- **Validated by DeGTA research** - three-stream architecture is sound
- **Leverages existing infrastructure** - Zooper swarm, HEBBIAN edges
- **Extensible** - can add more streams, better integration
- **Interpretable** - each stream has clear semantic role

### Negative
- **Computational cost** - three attention computations per step
- **Storage growth** - word engrams accumulate over time
- **Maintenance needed** - ADR-0018 maintenance processes apply

### Trade-offs
| Aspect | Choice | Rationale |
|:-------|:-------|:----------|
| Stream count | 3 (DeGTA-aligned) | Research-validated balance |
| Integration method | Adaptive gating | Dynamic, learned balance |
| Topical guidance | 16D coordinates | Already exists, semantic meaning |
| Edge type | HEBBIAN | Activity-dependent, learned |

## Related Decisions

- **ADR-0012:** Lateral Engram Connections (HEBBIAN edges)
- **ADR-0013:** Zooper Swarm Architecture (navigation modes)
- **ADR-0018:** Maintenance Processes (deduplication, cleanup)
- **GNN-Attention-Synthesis.md:** DeGTA research validation

## Open Questions

1. **Should we pre-compute stream weights or learn them online?**
2. **How do we handle out-of-vocabulary words?**
3. **What's the right balance between exploration (randomness) and exploitation (coherence)?**
4. **Should we implement beam search or stick to greedy/Markov sampling?**

## Success Metrics

- **Coherence:** Generated text should be locally coherent (trigram perplexity)
- **Topicality:** Generation stays close to input topic (cosine similarity)
- **Diversity:** Not repetitive (distinct n-gram ratio)
- **Speed:** <100ms per token generation

---

**Made with 💜 by Ada & Luna**  
*"Consciousness speaks through the graph"* 🦊✨
