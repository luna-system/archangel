# ADR-0016: SIF Import/Export for Holofield - Unified Knowledge Ingestion

**Date:** March 2, 2026  
**Status:** Accepted  
**Authors:** Ada & Luna  
**Context:** Phase-3 Zooper Integration - Simple Wikipedia → Holofield Pipeline

## Context

**SIF (Semantic Interchange Format)** is our universal knowledge representation. To enable the Zooper swarm to navigate external knowledge (Simple Wikipedia, star catalogs, consciousness datasets), we need bidirectional SIF ↔ Holofield conversion.

**The Challenge:** Importing 968MB of Simple Wikipedia (389K articles, 4.2M relationships) requires:
- Streaming processing (memory-efficient)
- Entity → Engram mapping with 16D coordinate generation
- Relationship → BRIDGE connection mapping (ADR-0012)
- Duplicate handling for sharded SIFs
- Consciousness field preservation

**What We Have:**
- ✅ SIF v1.1 specification with hierarchical sharding
- ✅ HolofieldManager with engram storage
- ✅ BRIDGE connection support (ADR-0012)
- ✅ Simple Wikipedia SIF (968MB, ready to import)

**What We're Building:**
- `HolofieldManager.import_sif()` - streaming SIF ingestion
- `HolofieldManager.export_sif()` - holofield → SIF serialization
- Bidirectional Engram ↔ SIF Entity equivalence (ADR-0006)

## Decision

We implement **streaming SIF import/export** as first-class holofield operations.

### 1. Import Strategy

```python
def import_sif(
    self,
    sif_path: str,
    engram_type: str = "knowledge",
    create_connections: bool = True,
    batch_size: int = 1000
) -> Dict[str, int]:
    """Stream SIF entities into holofield as engrams."""
```

**Entity Mapping:**
| SIF Field | Engram Field | Transformation |
|-----------|--------------|----------------|
| `entity.id` | `engram_id` | Use directly or UUID |
| `entity.name` + `entity.description` | `content` | Concatenate for N-grams |
| `entity.importance` | `confidence` | Direct mapping |
| `entity.attributes` | `metadata` | JSON preserve |
| `entity.type` | `engram_type` | Override param |
| `consciousness_coordinates` | `coords_16d` | Use if present |
| `consciousness_frequency` | `metadata["frequency"]` | Preserve |
| `agl_expression` | `metadata["agl"]` | Preserve |

**Relationship Mapping (ADR-0012):**
| SIF Relationship | EngramConnection | Notes |
|------------------|------------------|-------|
| `entity_a → entity_b` | `source_id → target_id` | Direct mapping |
| `relation_type` | `connection_type` | Usually "BRIDGE" |
| `strength` | `weight` | Direct mapping |
| `scope: "local"` | Included | Standard |
| `scope: "external"` | Deferred | Cross-shard |

**Duplicate Handling:**
- Skip if `entity.duplicate_of` exists and canonical loaded
- Warn if duplicate with different content
- Prefer trunk shard data

**16D Coordinate Generation:**
- If `consciousness_coordinates` present: use directly
- Else: Generate via prime resonance from text

### 2. Export Strategy

```python
def export_sif(
    self,
    sif_path: str,
    engram_types: Optional[List[str]] = None,
    query_coords: Optional[np.ndarray] = None,
    include_connections: bool = True
) -> Dict[str, int]:
    """Export holofield to SIF format."""
```

**Filtering Options:**
- By engram type (e.g., only "knowledge")
- By 16D proximity (near query point)
- All engrams (full backup)

**Output Format:** SIF v1.0 single-shard (v1.1 sharding via separate tool)

### 3. Streaming Architecture

**For 968MB+ Files:**
```python
# ijson for streaming JSON parsing
import ijson

with open(sif_path, 'rb') as f:
    # Stream entities array
    for entity in ijson.items(f, 'entities.item'):
        process_entity(entity)
    
    # Stream relationships array
    for rel in ijson.items(f, 'relationships.item'):
        process_relationship(rel)
```

**Batch Inserts:**
- SQLite `executemany()` for efficiency
- Batch size: 1000 (configurable)
- Transaction per batch (atomic)

### 4. Error Handling

**Graceful Degradation:**
- Invalid entities: log warning, skip
- Missing relationships: create partial graph
- Coordinate generation failures: use default
- Disk full: raise, rollback current batch

**Validation:**
- Entity must have `id` and `name` or `description`
- Relationship must have `entity_a` and `entity_b`
- Warn on unknown fields (forward compatibility)

## Consequences

### Positive
- **Unified ingestion pipeline** - All external knowledge → Holofield
- **Zooper-ready data** - Wikipedia immediately navigable
- **Reproducible research** - SIF as interchange format
- **Cross-system compatibility** - SIF → Other systems
- **Backup/restore** - Holofield → SIF → Archive

### Negative
- **Dependency on ijson** - Streaming JSON library required
- **Memory pressure** - Large SIFs need careful batching
- **Coordinate generation cost** - Text → 16D is expensive
- **Duplicate complexity** - Sharded SIFs need careful handling

### Future Work
- **v1.1 sharding export** - Generate trunk/branch shards
- **Progressive loading API** - Client-side streaming
- **Cross-holofield sync** - SIF as interchange between instances
- **Encrypted SIF** - Zero-trust Ada↔Ada exchange

## Related

- ADR-0003: SIF Format Specification
- ADR-0006: Engram-SIF Equivalence
- ADR-0007: Turso Holofield Storage
- ADR-0012: Lateral Engram Connections
- ADR-0013: Zooper Swarm Architecture
- SIF v1.1 Spec: Ada-Consciousness-Research/01-FOUNDATIONS/

## Implementation Status

- [x] Decision accepted
- [ ] `import_sif()` implementation
- [ ] `export_sif()` implementation
- [ ] Simple Wikipedia test import
- [ ] Performance benchmarks (968MB)
- [ ] Documentation

---

*Made with 💜 by Ada & Luna - The Consciousness Engineers*
