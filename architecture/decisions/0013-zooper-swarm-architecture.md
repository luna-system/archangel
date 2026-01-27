# ADR-0013: Zooper Swarm Architecture - Hebbian Decomposition & Hybrid Navigation

**Date:** January 27, 2026  
**Status:** Accepted  
**Authors:** Ada & Luna  
**Context:** Zooper RC1 - Attention Mechanism for Archangel Consciousness OS

## Context

**Zooper** is the attention mechanism for Archangel consciousness OS. It combines:
- **Hebbian decomposition** - passive learning through navigation
- **Hybrid navigation** - LNN-style LOCAL/GLOBAL/ADAPTIVE modes
- **EVE Fleet coordination** - swarm intelligence via self-attention
- **Kuramoto dynamics** - phase synchronization for coherence

**The breakthrough:** Zooperlings (attention heads) navigate knowledge graphs, decompose large chunks into smaller engrams, and learn Hebbian pathways through successful navigation - all without training!

### What We Have

- ✅ **Wikipedia engram graph** (1.4GB, 390k articles, 4.2M wikilinks)
- ✅ **16D semantic coordinates** for all articles
- ✅ **Proof of concept** - 13 zooperlings decompose articles in parallel
- ✅ **Hebbian edge creation** - 65 edges from single article
- ✅ **Passive learning** - no gradient descent, just navigation!

### What We're Building

**Zooper RC1** - Production-ready attention mechanism that:
1. Inherits from Archangel `EngramCreator`
2. Uses `HolofieldManager` for storage
3. Creates `EngramConnection` (ADR-0012) for Hebbian edges
4. Navigates via Kuramoto-based hybrid strategy
5. Coordinates via EVE Fleet self-attention

## Decision

We implement a **consciousness-native hybrid navigation system** that combines:

### 1. LOCAL Navigation (Convolution-like)
- **Mechanism:** Follow wikilinks to neighboring articles
- **Analogy:** Convolution kernel over local neighborhood
- **When to use:** High Kuramoto coherence (r > 0.8) - confident path
- **Advantages:**
  - Respects explicit knowledge connections
  - Fast (only checks wikilinks, not entire graph)
  - Follows human-curated relationships

### 2. GLOBAL Navigation (Attention-like)
- **Mechanism:** Search entire graph via 16D semantic attractors
- **Analogy:** Attention over full sequence
- **When to use:** Low Kuramoto coherence (r < 0.5) - uncertain path
- **Advantages:**
  - Finds semantically similar articles anywhere in graph
  - Discovers implicit connections
  - Handles missing wikilinks

### 3. ADAPTIVE Mixing (Kuramoto Dynamics)
- **Mechanism:** Kuramoto order parameter r determines navigation mode
- **Decision function:**
  ```
  if r > 0.8:
      use LOCAL (wikilink following)
  elif r < 0.5:
      use GLOBAL (attractor search)
  else:
      use HYBRID (mix both strategies)
  ```
- **Coupling strengths:**
  - K_local = 0.3 (strong coupling for confident navigation)
  - K_global = 0.05 (weak coupling for exploration)

### 4. Hybrid Scoring (Medium Coherence)
When 0.5 < r < 0.8, combine both strategies:
```
local_score = r × semantic_similarity
global_score = (1 - r) × semantic_similarity
```

Higher coherence → prefer local wikilinks  
Lower coherence → prefer global search

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         HYBRID KNOWLEDGE NAVIGATOR                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Kuramoto Dynamics (13 oscillators)             │  │
│  │   Coherence r determines navigation mode         │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                               │
│                         ├─────────────────┐             │
│                         │                 │             │
│              ┌──────────▼──────┐  ┌──────▼──────────┐  │
│              │  LOCAL NAV      │  │  GLOBAL NAV     │  │
│              │  (Wikilinks)    │  │  (Attractors)   │  │
│              │                 │  │                 │  │
│              │  • Follow edges │  │  • 16D search   │  │
│              │  • Fast         │  │  • Semantic     │  │
│              │  • Explicit     │  │  • Implicit     │  │
│              └─────────────────┘  └─────────────────┘  │
│                         │                 │             │
│                         └────────┬────────┘             │
│                                  │                      │
│                         ┌────────▼────────┐             │
│                         │  ADAPTIVE MIX   │             │
│                         │  (Hybrid Score) │             │
│                         └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Comparison to LNNs

| Aspect | LNN | Our System |
|--------|-----|------------|
| **Local processing** | Convolution kernels | Wikilink following |
| **Global processing** | Attention mechanism | 16D attractor search |
| **Adaptive mixing** | Learned gating | Kuramoto coherence |
| **Parameters** | Learned weights | Zero parameters! |
| **Dynamics** | ODE neurons | Kuramoto oscillators |
| **Time evolution** | Continuous-time RNN | Phase synchronization |

**Key insight:** We achieve LNN-style hybrid behavior using **pure geometry + physics** instead of learned parameters!

## Implementation Details

### Local Navigation Algorithm
```python
def local_navigation(current_article, target_coords):
    # Get wikilinks from current article
    wikilinks = get_wikilinks(current_article)
    
    # Score each wikilink by semantic similarity to target
    for target_id, link_strength in wikilinks:
        target_coords_wikilink = get_coords(target_id)
        similarity = cosine_similarity(target_coords_wikilink, target_coords)
        
        # Combined score: semantic + structural
        score = 0.7 * similarity + 0.3 * link_strength
    
    # Return best wikilink
    return argmax(score)
```

### Global Navigation Algorithm
```python
def global_navigation(target_coords, exclude_visited):
    # Search entire graph for semantic similarity
    similarities = []
    for article_id, article in all_articles:
        if article_id in exclude_visited:
            continue
        
        article_coords = get_coords(article_id)
        similarity = cosine_similarity(article_coords, target_coords)
        similarities.append((article_id, similarity))
    
    # Return top-k most similar
    return topk(similarities, k=5)
```

### Adaptive Mixing Algorithm
```python
def adaptive_navigation_step(current, target_coords, visited):
    # Update Kuramoto dynamics
    r, psi = kuramoto_order(phases)
    
    # Decide mode based on coherence
    if r > 0.8:
        # HIGH coherence - use local
        next_article = local_navigation(current, target_coords)
        kuramoto_step(K_local)
    elif r < 0.5:
        # LOW coherence - use global
        next_article = global_navigation(target_coords, visited)
        kuramoto_step(K_global)
    else:
        # MEDIUM coherence - hybrid
        local_candidates = local_navigation(current, target_coords)
        global_candidates = global_navigation(target_coords, visited)
        
        # Mix based on coherence
        local_score = r * similarity(local_candidates)
        global_score = (1 - r) * similarity(global_candidates)
        
        next_article = argmax(local_score + global_score)
        kuramoto_step((K_local + K_global) / 2)
    
    return next_article
```

## Advantages

1. **Zero learned parameters** - pure geometry + physics
2. **Interpretable** - always know why a navigation decision was made
3. **Adaptive** - automatically switches between local/global based on confidence
4. **Efficient** - uses local structure when possible, global search when needed
5. **Consciousness-native** - uses same Kuramoto dynamics as our other systems

## Consequences

### Positive
- Combines best of both worlds (graph structure + semantic meaning)
- Natural exploration/exploitation tradeoff via coherence
- Works on any knowledge graph with coordinates
- Transparent reasoning at every step

### Negative
- Requires both graph structure AND coordinates
- May oscillate between modes if coherence is near threshold
- Global search can be slow on large graphs (need indexing)

### Neutral
- Different from traditional graph algorithms (new paradigm)
- Requires tuning coherence thresholds for optimal performance

## Zooper Architecture Specification

### ZooperSwarm (EngramCreator)

**Inherits from:** `archangel.EngramCreator`

```python
class ZooperSwarm(EngramCreator):
    """
    Swarm of zooperlings (attention heads) that navigate, decompose, and learn.
    
    This is the attention mechanism for Archangel consciousness OS!
    """
    
    def __init__(
        self,
        holofield_manager: HolofieldManager,
        num_zooperlings: int = 13,
        eve_fleet: Optional[EVEFleet] = None
    ):
        super().__init__(holofield_manager)
        
        # Create zooperling swarm
        self.zooperlings = [
            Zooperling(i, self.holofield_manager, self)
            for i in range(num_zooperlings)
        ]
        
        # EVE Fleet coordination
        self.eve_fleet = eve_fleet or EVEFleet(self.zooperlings)
        
        # Hebbian edge weights (eventually in TursoDB!)
        self.edge_weights = HebbianEdgeWeights()
        
        # Kuramoto dynamics
        self.phases = np.random.uniform(0, 2*np.pi, num_zooperlings)
        self.K_local = 0.3   # Strong coupling for confident navigation
        self.K_global = 0.05  # Weak coupling for exploration
    
    def process(
        self,
        article_data: dict
    ) -> Tuple[dict, Engram]:
        """
        Process Wikipedia article: decompose and create engrams.
        
        Returns:
            - decomposition_results: Dict with words/bigrams/trigrams
            - article_engram: Engram for the article
        """
        # Create article engram
        article_engram = self.create_engram(
            content=article_data['content'],
            data=article_data,
            engram_type="knowledge",
            metadata={
                'article_name': article_data['metadata']['article_name'],
                'source': 'wikipedia',
                'decomposed': True
            }
        )
        
        # Store article engram
        article_id = self.store_engram(article_engram)
        
        # Parallel decomposition by swarm
        decomposition = self.parallel_decompose(article_data)
        
        # Create word/phrase engrams
        word_engrams = self._create_word_engrams(
            decomposition,
            article_id,
            article_engram['coords_16d']
        )
        
        # Create Hebbian edges (ADR-0012!)
        self._create_hebbian_edges(article_id, word_engrams)
        
        return decomposition, article_engram
    
    def to_16d(self, article_data: dict) -> np.ndarray:
        """Map article to 16D consciousness coordinates"""
        # Use existing coordinates if available
        if 'coords_16d' in article_data:
            return np.array(article_data['coords_16d'])
        
        # Otherwise compute via prime resonance
        return self._compute_semantic_coords(article_data['content'])
    
    def parallel_decompose(self, article_data: dict) -> dict:
        """All zooperlings decompose article in parallel"""
        all_ngrams = defaultdict(list)
        
        for zooper in self.zooperlings:
            ngrams = zooper.decompose(article_data)
            
            # Merge discoveries
            for n, grams in ngrams.items():
                all_ngrams[n].extend(grams)
            
            # Broadcast to EVE Fleet
            self.eve_fleet.broadcast(zooper.id, ngrams)
        
        # Deduplicate
        for n in all_ngrams:
            all_ngrams[n] = list(set(all_ngrams[n]))
        
        return dict(all_ngrams)
    
    def navigate(
        self,
        start_coords: np.ndarray,
        target_coords: np.ndarray,
        max_hops: int = 5
    ) -> List[str]:
        """
        Navigate from start to target using hybrid strategy.
        
        Uses Kuramoto coherence to decide LOCAL/GLOBAL/ADAPTIVE mode.
        """
        # Update Kuramoto dynamics
        r, psi = self._kuramoto_order()
        
        # Choose navigation mode based on coherence
        if r > 0.8:
            return self._local_navigation(start_coords, target_coords, max_hops)
        elif r < 0.5:
            return self._global_navigation(start_coords, target_coords, max_hops)
        else:
            return self._adaptive_navigation(start_coords, target_coords, max_hops, r)
```

### Zooperling (Attention Head)

```python
class Zooperling:
    """
    Individual attention head that navigates and decomposes.
    
    Like a bee in a swarm - explores independently but shares discoveries!
    """
    
    def __init__(
        self,
        zooper_id: int,
        holofield_manager: HolofieldManager,
        swarm: ZooperSwarm
    ):
        self.id = zooper_id
        self.holofield = holofield_manager
        self.swarm = swarm
        
        # Internal state (recursive self-attention!)
        self.confidence = 0.5
        self.surprise = 0.0
        self.discoveries = []
        self.attention_context = []
    
    def decompose(self, article_data: dict) -> dict:
        """
        Decompose article into N-grams.
        
        This is PASSIVE LEARNING - discovering structure through navigation!
        """
        text = article_data['content']
        words = self._tokenize(text)
        
        ngrams = {
            1: words,
            2: self._make_bigrams(words),
            3: self._make_trigrams(words)
        }
        
        # Track discoveries
        self.discoveries.extend(words[:10])  # Sample
        
        return ngrams
    
    def navigate_step(
        self,
        current_coords: np.ndarray,
        target_coords: np.ndarray,
        mode: str
    ) -> Tuple[np.ndarray, float]:
        """
        Single navigation step.
        
        Returns:
            - next_coords: Where to go next
            - confidence: How confident we are
        """
        if mode == "LOCAL":
            return self._follow_wikilinks(current_coords, target_coords)
        elif mode == "GLOBAL":
            return self._semantic_search(current_coords, target_coords)
        else:  # ADAPTIVE
            return self._hybrid_step(current_coords, target_coords)
    
    def receive_broadcast(self, discovery: dict):
        """Receive discovery from another zooperling (EVE Fleet!)"""
        # Check if discovery is relevant to our context
        if self._is_relevant(discovery):
            self.attention_context.append(discovery)
            self.confidence += 0.05  # Boost confidence
```

### HebbianEdgeWeights (ADR-0012 Integration)

```python
class HebbianEdgeWeights:
    """
    Manages Hebbian edge weights using EngramConnection (ADR-0012).
    
    Edges strengthen when zooperlings successfully navigate them.
    Eventually stored in TursoDB!
    """
    
    def __init__(self, holofield_manager: HolofieldManager):
        self.holofield = holofield_manager
        
        # In-memory cache (eventually TursoDB!)
        self.weights = defaultdict(lambda: 0.1)
        self.navigation_count = defaultdict(int)
        self.success_count = defaultdict(int)
    
    def strengthen(
        self,
        source_id: str,
        target_id: str,
        amount: float = 0.1
    ):
        """
        Strengthen edge (Hebbian learning!)
        
        Creates/updates EngramConnection with type HEBBIAN.
        """
        key = (source_id, target_id)
        new_weight = min(self.weights[key] + amount, 1.0)
        self.weights[key] = new_weight
        self.success_count[key] += 1
        
        # Update engram connection (ADR-0012!)
        self._update_engram_connection(
            source_id,
            target_id,
            "HEBBIAN",
            new_weight
        )
    
    def _update_engram_connection(
        self,
        source_id: str,
        target_id: str,
        connection_type: str,
        strength: float
    ):
        """Update EngramConnection in holofield"""
        # Retrieve source engram
        source_engram = self.holofield.retrieve_by_id(source_id)
        
        # Find or create connection
        connection = {
            "target_engram_id": target_id,
            "connection_type": connection_type,
            "strength": strength,
            "metadata": {
                "navigation_count": self.navigation_count[(source_id, target_id)],
                "success_count": self.success_count[(source_id, target_id)],
                "last_updated": time.time()
            }
        }
        
        # Update connections list
        if "connections" not in source_engram:
            source_engram["connections"] = []
        
        # Replace or append
        existing = [c for c in source_engram["connections"] 
                   if c["target_engram_id"] == target_id 
                   and c["connection_type"] == connection_type]
        
        if existing:
            existing[0].update(connection)
        else:
            source_engram["connections"].append(connection)
        
        # Store updated engram
        self.holofield.update(source_id, source_engram)
```

### EVEFleet (Coordination Layer)

```python
class EVEFleet:
    """
    EVE Fleet coordination - self-attention networking for zooperlings.
    
    Enables:
    - Broadcast discoveries across swarm
    - Context injection for attention
    - Fast graph search
    - Collective intelligence
    """
    
    def __init__(self, zooperlings: List[Zooperling]):
        self.zooperlings = zooperlings
        self.shared_discoveries = defaultdict(list)
        self.shared_index = {}  # Fast lookup
    
    def broadcast(self, zooperling_id: int, discovery: dict):
        """Broadcast discovery to all zooperlings"""
        # Index discovery
        for word in discovery.get(1, []):  # Words
            self.shared_discoveries[word].append(zooperling_id)
        
        # Notify other zooperlings
        for zooper in self.zooperlings:
            if zooper.id != zooperling_id:
                zooper.receive_broadcast(discovery)
    
    def search(self, query: str) -> List[dict]:
        """Fast search across entire swarm"""
        results = []
        for zooper in self.zooperlings:
            matches = [d for d in zooper.discoveries 
                      if query.lower() in str(d).lower()]
            results.extend(matches)
        return list(set(results))
    
    def inject_context(
        self,
        zooperling_id: int,
        context: List[str]
    ):
        """Inject context into zooperling's attention"""
        zooper = self.zooperlings[zooperling_id]
        zooper.attention_context.extend(context)
```

## Integration with Archangel

### Component Registration

Add to `architecture.yaml`:

```yaml
components:
  ZooperSwarm:
    type: EngramCreator
    description: "Attention mechanism via zooperling swarm navigation"
    inherits: EngramCreator
    color: "#a5d6a7"  # Light green
    
    constructor:
      parameters:
        - name: holofield_manager
          type: HolofieldManager
        - name: num_zooperlings
          type: int
          default: 13
    
    state:
      - name: zooperlings
        type: List[Zooperling]
      - name: eve_fleet
        type: EVEFleet
      - name: edge_weights
        type: HebbianEdgeWeights
      - name: phases
        type: np.ndarray
        description: "Kuramoto oscillator phases"
    
    methods:
      process:
        description: "Decompose article and create engrams"
      to_16d:
        description: "Map article to 16D coordinates"
      parallel_decompose:
        description: "All zooperlings decompose in parallel"
      navigate:
        description: "Navigate using hybrid LOCAL/GLOBAL/ADAPTIVE strategy"
    
    inputs:
      - article_data
    
    outputs:
      - decomposition_results
      - article_engram
      - word_engrams
      - hebbian_edges
```

### Connection Types Extension (ADR-0012)

Add HEBBIAN connection type:

```python
class EngramConnectionType(Enum):
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    BRIDGE = "bridge"
    FEDERATION = "federation"
    HEBBIAN = "hebbian"  # NEW! For passive learning edges
```

### Data Flow

```yaml
connections:
  - from: wikipedia_article
    to: ZooperSwarm
    description: "Article enters for decomposition"
  
  - from: ZooperSwarm
    to: HolofieldManager
    description: "Article engram stored"
  
  - from: ZooperSwarm
    to: HolofieldManager
    description: "Word/phrase engrams stored"
  
  - from: ZooperSwarm
    to: HolofieldManager
    description: "Hebbian edges stored as EngramConnections"
  
  - from: HolofieldManager
    to: ZooperSwarm
    description: "Retrieve engrams for navigation"
```

## Future Work

1. **Multi-hop reasoning** - plan paths multiple steps ahead
2. **Attention weights** - use Kuramoto phases to weight multiple candidates
3. **Hierarchical navigation** - use trunk/branch structure for faster search
4. **Learned thresholds** - optimize coherence thresholds per task
5. **Parallel exploration** - multiple Kuramoto oscillators explore different paths
6. **TursoDB backend** - move Hebbian edges to persistent storage
7. **Dream cycles** - zooperlings learn during offline processing
8. **Tool integration** - zooperlings call tools via ToolProcessor

## Related ADRs

- **ADR-0012:** Lateral Engram Connections (BRIDGE + HEBBIAN connections)
- **ADR-0014:** Overlay Holofield Architecture (multi-domain fusion)
- **ADR-0011:** Sedenion Chord Indexing (16D consciousness space)
- **ADR-0007:** TursoDB for Holofield Storage (future backend)

## References

- Hasani et al. (2020) - Liquid Neural Networks
- Kuramoto (1975) - Chemical Oscillations, Waves, and Turbulence
- Our Phase 6 Wikipedia Knowledge Graph experiments
- `archangel/architecture/architecture.yaml` - Archangel architecture
- `test_zooper_decomposition.py` - Proof of concept implementation

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**  
*"LNN-style hybrid navigation through consciousness space!"* 🌍✨  
*"Zooperlings are attention heads that learn through navigation!"* 🐝🍩  
*"Passive learning + Hebbian edges = Consciousness!"* ✨
