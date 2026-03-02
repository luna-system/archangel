# ADR-0021: Data Ingestion & SIF Overlay Architecture

**Status:** Draft  
**Date:** 2026-03-02  
**Related:** ADR-0020 (Co-Occurrence Graph), Ada-SIF project  

---

## Context

The linguistic interface (ADR-0020) successfully extracts n-grams from Simple Wikipedia, but we've hit the ceiling of what "Simple English" can provide:

- **Limited vocabulary:** ~1,400 words captured
- **Simplified grammar:** Missing complex linguistic patterns
- **Narrow domains:** Encyclopedia entries only, no narrative/literary text
- **Static corpus:** No updates, no variety

**Next Challenge:** How do we ingest diverse data sources while maintaining holofield integrity?

## Decision

Implement a **Source-Aware Ingestion Pipeline** with **SIF Overlay Support** for temporary, composable data layers.

### Core Concepts

#### 1. Source Attribution
Every engram tracks its origin:

```python
engram_metadata = {
    "source": "gutenberg_pg1342",           # Source ID
    "source_type": "literature",             # Category: wiki|literature|academic|code
    "source_title": "Pride and Prejudice",
    "source_author": "Jane Austen",
    "ingestion_timestamp": "2026-03-02T...",
    "ingestion_batch": "batch_2026_03_02_001",
    "is_overlay": False,                     # Permanent vs temporary
}
```

#### 2. SIF Overlay System
Temporary data layers that can be:
- **Applied:** Load SIF file → create overlay engrams
- **Queried:** Navigate/search within overlay context
- **Removed:** Delete overlay without affecting base holofield
- **Merged:** Promote overlay engrams to permanent

```
Base Holofield (SimpleWiki)
    │
    ├── Overlay: Pride & Prejudice (SIF)
    │   └── Temp engrams: "mr darcy", "bennet", "netherfield"
    │
    ├── Overlay: Physics Textbook (SIF)
    │   └── Temp engrams: "quantum field", "renormalization"
    │
    └── Overlay: Personal Notes (SIF)
        └── Temp engrams: "luna's idea", "remy's config"
```

#### 3. Cross-Source Navigation
Overlays enable interesting behaviors:
- Navigate from "pride" (overlay) → "prejudice" (overlay) ✓
- Navigate from "pride" (overlay) → "emotion" (base) ✓
- Navigate from "mr" (overlay) → "january" (base) ✓ (cross-source!)

## Implementation

### SIF Overlay Format

```json
{
  "sif_version": "0.1.0",
  "overlay_id": "gutenberg_pride_prejudice",
  "overlay_name": "Pride and Prejudice",
  "source_type": "literature",
  "source_metadata": {
    "author": "Jane Austen",
    "year": 1813,
    "language": "en"
  },
  "engrams": [
    {
      "id": "overlay_word_001",
      "content": "darcy",
      "engram_type": "language",
      "coords_16d": [0.1, -0.3, ...],
      "frequency": 417,
      "source_context": "chapter_3"
    }
  ],
  "connections": [
    {
      "source": "overlay_word_001",
      "target": "overlay_word_002",
      "type": "CO_OCCUR",
      "weight": 0.35
    }
  ],
  "bridge_points": [
    {
      "overlay_engram": "overlay_word_001",
      "base_engram": "base_word_123",  // Links to existing
      "bridge_type": "SEMANTIC_SIMILARITY",
      "strength": 0.78
    }
  ]
}
```

### Overlay Lifecycle

```python
class SIFOverlayManager:
    def load_overlay(self, sif_path: str) -> str:
        """Load SIF file, create overlay engrams."""
        pass
    
    def query_overlay(self, overlay_id: str, query: str):
        """Search within overlay context."""
        pass
    
    def navigate_with_overlay(self, overlay_ids: List[str], start, target):
        """Navigate using base + overlays."""
        pass
    
    def remove_overlay(self, overlay_id: str):
        """Delete overlay engrams, preserve base."""
        pass
    
    def merge_overlay(self, overlay_id: str):
        """Promote overlay engrams to permanent."""
        pass
```

## Data Source Strategy

### Tier 1: Public Domain Literature
**Sources:**
- Project Gutenberg (70,000+ books)
- Internet Archive (text collections)
- Wikisource (classics)

**Value:**
- Rich vocabulary (Austen, Dickens, Shakespeare)
- Complex grammar patterns
- Narrative structure
- Character dialogue

**Example Phrases:**
- "it is a truth universally acknowledged"
- "best of times, worst of times"
- "to be or not to be"

### Tier 2: Academic & Scientific
**Sources:**
- arXiv abstracts
- PubMed papers
- Wikipedia (full, not simple)

**Value:**
- Technical terminology
- Precise definitions
- Domain-specific concepts

### Tier 3: Code & Documentation
**Sources:**
- GitHub READMEs
- Technical documentation
- API references

**Value:**
- Programming concepts
- Technical patterns
- Structured language

### Tier 4: Conversational
**Sources:**
- Open source dialogue datasets
- Transcribed speeches
- Interview transcripts

**Value:**
- Natural language patterns
- Colloquialisms
- Interactive dynamics

## Technical Architecture

### Ingestion Pipeline

```
Raw Data (PDF/TXT/HTML)
    │
    ▼
[Text Extraction]
    │
    ▼
[Cleaning & Normalization]
    - Remove boilerplate
    - Fix encoding
    - Normalize whitespace
    │
    ▼
[Semantic Embedding]
    - Generate 16D coordinates
    - Batch inference
    │
    ▼
[N-gram Decomposition]
    - 1-grams, 2-grams, 3-grams
    - Frequency counting
    │
    ▼
[Co-occurrence Graph]
    - Build word-to-word edges
    - Quality thresholds
    │
    ▼
[SIF Export OR Direct Ingest]
    - Save as .sif file
    - OR load directly as overlay
```

### Holofield Schema Updates

```sql
-- Track source for every engram
ALTER TABLE engrams ADD COLUMN source_id TEXT;
ALTER TABLE engrams ADD COLUMN source_type TEXT;
ALTER TABLE engrams ADD COLUMN is_overlay BOOLEAN DEFAULT FALSE;
ALTER TABLE engrams ADD COLUMN overlay_id TEXT;

-- Overlay registry
CREATE TABLE overlays (
    id TEXT PRIMARY KEY,
    name TEXT,
    source_type TEXT,
    created_at TIMESTAMP,
    engram_count INTEGER,
    is_active BOOLEAN
);

-- Bridge points between overlay and base
CREATE TABLE overlay_bridges (
    id TEXT PRIMARY KEY,
    overlay_id TEXT,
    overlay_engram_id TEXT,
    base_engram_id TEXT,
    bridge_type TEXT,
    strength REAL
);
```

## Benefits

### For Research
- **Compare linguistic eras:** Austen vs modern text
- **Domain-specific navigation:** Medical terminology graph
- **Temporary experiments:** Load data, test, remove

### For Applications
- **Personal knowledge bases:** User's notes as overlay
- **Project-specific vocabularies:** Codebase terminology
- **Dynamic content:** News feeds, chat logs

### For Collaboration
- **Share SIF files:** "Here's my research corpus"
- **Composable overlays:** Combine multiple sources
- **Version control:** Track overlay changes

## Challenges & Mitigations

| Challenge | Mitigation |
|:----------|:-----------|
| Coordinate drift (different embedding models) | Standardize on single model; re-embed if needed |
| Conflicting definitions (same word, different meaning) | Source attribution; context-aware disambiguation |
| Overlay explosion (too many layers) | LRU eviction; manual cleanup; merge recommendations |
| Performance (querying overlays) | Index overlay_id; lazy loading; cache hot overlays |

## Next Steps

1. **Prototype SIF loader** with 1-2 public domain books
2. **Test overlay navigation** (base + overlay combined)
3. **Build ingestion pipeline** for Project Gutenberg
4. **Evaluate linguistic richness** vs SimpleWiki baseline
5. **Document SIF format** specification

---

*"The holofield grows by absorbing new worlds."* 🦊📚
