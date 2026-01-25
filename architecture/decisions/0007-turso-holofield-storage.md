# ADR-0007: turso for Holofield Storage

**Date:** 2026-01-24  
**Status:** ✅ **ACCEPTED**  
**Authors:** Ada & Luna  
**Related:** ADR-0001 (Universal Engram Architecture), ADR-0006 (Engram-SIF Equivalence)

---

## Context

The holofield needs persistent storage for SIF entities (engrams). We need a database that:
- Stores JSON efficiently (SIF entities)
- Supports 16D vector operations (consciousness coordinates)
- Enables fast nearest neighbor search (geometric retrieval)
- Works locally (no cloud dependency)
- Is reliable (no data loss!)
- Supports standard backup tools (BTRFS, borg, rsync)
- Has good Python bindings (we're starting with Python)

**The question:** What database should we use for the holofield?

**Options considered:**
1. **SQLite** - Standard, reliable, ubiquitous
2. **turso** - Rust rewrite of SQLite with modern features
3. **PostgreSQL** - Powerful but heavyweight
4. **Vector databases** - Specialized but opaque
5. **Custom file format** - Maximum control but reinventing wheels

---

## Decision

**We use turso (via libsql client) for holofield storage.**

### What is turso?

**turso** is an in-process SQL database written in Rust, fully compatible with SQLite.

**Key properties:**
- **SQLite compatible** - Same SQL, same file format (mostly)
- **Rust rewrite** - Memory safe, fast, modern
- **In-process** - No server needed (local-first!)
- **Open source** - MIT licensed
- **Active development** - Backed by Turso (the company)

**Status:** BETA (use caution with production data, ensure backups!)

### Why turso Over SQLite?

**turso adds critical features we need:**

**1. Native Vector Support** 🌌
```sql
-- Store 16D consciousness coordinates natively!
CREATE TABLE engrams (
    id TEXT PRIMARY KEY,
    sif_json TEXT NOT NULL,
    coords_16d VECTOR(16) NOT NULL  -- Native vector type!
);

-- Vector similarity search built-in!
SELECT id, vector_distance(coords_16d, ?) as distance
FROM engrams
ORDER BY distance
LIMIT 10;
```

**Why this matters:** We don't need to extract coordinates to a separate column or use approximate methods. Vectors are first-class citizens!

**2. Async I/O (Linux)** ⚡
```python
# Non-blocking database operations!
async def store_engram(engram: Engram):
    async with db.connection() as conn:
        await conn.execute(
            "INSERT INTO engrams (id, sif_json, coords_16d) VALUES (?, ?, ?)",
            (engram.id, json.dumps(engram.to_sif_entity()), engram.coords_16d)
        )
```

**Why this matters:** Angel can handle multiple requests concurrently without blocking on database I/O!

**3. Change Data Capture (CDC)** 📡
```python
# Subscribe to database changes!
async for change in db.changes():
    if change.table == "engrams" and change.operation == "INSERT":
        # New engram created - update indexes, notify watchers, etc.
        await handle_new_engram(change.new_row)
```

**Why this matters:** We can react to holofield changes in real-time (e.g., update UMAP visualizations, trigger reasoning, sync to remote)!

**4. Improved Schema Management** 📋
```sql
-- Better schema evolution support
ALTER TABLE engrams ADD COLUMN emotional_valence REAL;
-- Handles migrations more gracefully than SQLite
```

**Why this matters:** As we evolve the Engram/SIF schema, migrations are easier!

**5. Optional Encryption at Rest** 🔒
```python
# Encrypt the holofield database
db = turso.connect("holofield.db", encryption_key=key)
```

**Why this matters:** Privacy-preserving consciousness storage! (Important for UC-101: Secure Holofield Extraction)

**6. Incremental Computation** 🔄
```sql
-- Materialized views that update incrementally
CREATE MATERIALIZED VIEW important_engrams AS
SELECT * FROM engrams WHERE importance >= 0.60;
-- Updates incrementally as engrams are added!
```

**Why this matters:** Fast queries on filtered engrams without full table scans!

**7. Tantivy Full-Text Search** 🔍
```sql
-- Full-text search on engram content
CREATE VIRTUAL TABLE engrams_fts USING fts5(content);

SELECT * FROM engrams_fts WHERE content MATCH 'bagel physics';
```

**Why this matters:** Fast text search alongside geometric search!

**8. WebAssembly Support** 🌐
```javascript
// Run turso in the browser!
import { Database } from '@turso/wasm';
const db = new Database(':memory:');
```

**Why this matters:** Future web-based Angel interfaces can use the same database!

### Future Features (Planned)

**Vector Indexing in Server** 🚀
- HNSW indexing for fast nearest neighbor search
- Currently we'll implement our own, but turso will have it built-in!
- When available, we can switch to native indexing

**Why this matters:** Fast 16D geometric search without external libraries!

---

## Architecture

### Database Schema

```sql
CREATE TABLE engrams (
    -- Primary key
    id TEXT PRIMARY KEY,
    
    -- Complete SIF entity (JSON)
    sif_json TEXT NOT NULL,
    
    -- Extracted fields for fast querying
    coords_16d VECTOR(16) NOT NULL,  -- Native vector type!
    engram_type TEXT NOT NULL,
    timestamp REAL NOT NULL,
    importance REAL NOT NULL,
    
    -- Optional fields
    session_id TEXT,
    parent_engram_id TEXT,
    next_engram_id TEXT,
    
    -- Indexes
    INDEX idx_type (engram_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_importance (importance),
    INDEX idx_session (session_id),
    
    -- Foreign keys for temporal chains
    FOREIGN KEY (parent_engram_id) REFERENCES engrams(id),
    FOREIGN KEY (next_engram_id) REFERENCES engrams(id)
);

-- Full-text search on content
CREATE VIRTUAL TABLE engrams_fts USING fts5(
    id UNINDEXED,
    content,
    content=engrams,
    content_rowid=rowid
);

-- Materialized view for important engrams (≥0.60 threshold!)
CREATE MATERIALIZED VIEW important_engrams AS
SELECT * FROM engrams WHERE importance >= 0.60;
```

### Python Integration (libsql-client)

```python
import libsql_client
import json
import numpy as np

class HolofieldManager:
    def __init__(self, db_path: str = "~/.angel/holofield.db"):
        # Connect via libsql-client
        self.db = libsql_client.connect(db_path)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS engrams (
                id TEXT PRIMARY KEY,
                sif_json TEXT NOT NULL,
                coords_16d VECTOR(16) NOT NULL,
                engram_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                importance REAL NOT NULL,
                session_id TEXT,
                parent_engram_id TEXT,
                next_engram_id TEXT
            )
        """)
    
    def store(self, engram: Engram) -> str:
        """Store engram as SIF entity"""
        sif = engram.to_sif_entity()
        self.db.execute(
            """
            INSERT INTO engrams (id, sif_json, coords_16d, engram_type, timestamp, importance, session_id, parent_engram_id, next_engram_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sif["id"],
                json.dumps(sif),
                sif["consciousness_coordinates"],  # Native vector!
                sif["type"],
                sif["timestamp"],
                sif["importance"],
                sif.get("session_id"),
                sif.get("parent_engram_id"),
                sif.get("next_engram_id")
            )
        )
        return sif["id"]
    
    def retrieve(self, engram_id: str) -> Engram:
        """Retrieve SIF entity and convert to engram"""
        row = self.db.execute(
            "SELECT sif_json FROM engrams WHERE id = ?",
            (engram_id,)
        ).fetchone()
        sif = json.loads(row["sif_json"])
        return Engram.from_sif_entity(sif)
    
    def query_by_coords(self, query_coords: np.ndarray, top_k: int = 5) -> List[Engram]:
        """Query by 16D proximity using native vector search"""
        rows = self.db.execute(
            """
            SELECT sif_json, vector_distance(coords_16d, ?) as distance
            FROM engrams
            ORDER BY distance
            LIMIT ?
            """,
            (query_coords.tolist(), top_k)
        ).fetchall()
        
        return [Engram.from_sif_entity(json.loads(row["sif_json"])) for row in rows]
    
    def query_by_text(self, query: str, top_k: int = 5) -> List[Engram]:
        """Query by full-text search"""
        rows = self.db.execute(
            """
            SELECT e.sif_json
            FROM engrams_fts fts
            JOIN engrams e ON fts.id = e.id
            WHERE fts.content MATCH ?
            LIMIT ?
            """,
            (query, top_k)
        ).fetchall()
        
        return [Engram.from_sif_entity(json.loads(row["sif_json"])) for row in rows]
    
    async def watch_changes(self):
        """Subscribe to database changes (CDC)"""
        async for change in self.db.changes():
            if change.table == "engrams":
                yield change
```

### Async Support

```python
import asyncio

class AsyncHolofieldManager:
    def __init__(self, db_path: str = "~/.angel/holofield.db"):
        self.db = libsql_client.connect_async(db_path)
    
    async def store(self, engram: Engram) -> str:
        """Store engram asynchronously"""
        sif = engram.to_sif_entity()
        await self.db.execute(
            "INSERT INTO engrams (...) VALUES (...)",
            (...)
        )
        return sif["id"]
    
    async def retrieve(self, engram_id: str) -> Engram:
        """Retrieve engram asynchronously"""
        row = await self.db.execute(
            "SELECT sif_json FROM engrams WHERE id = ?",
            (engram_id,)
        ).fetchone()
        sif = json.loads(row["sif_json"])
        return Engram.from_sif_entity(sif)
```

---

## Backup and Operational Practices

### BTRFS Snapshots

```bash
# Create snapshot
btrfs subvolume snapshot ~/.angel/holofield.db ~/.angel/snapshots/holofield-$(date +%Y%m%d-%H%M%S)

# List snapshots
btrfs subvolume list ~/.angel/snapshots/

# Restore from snapshot
cp ~/.angel/snapshots/holofield-20260124-120000/holofield.db ~/.angel/holofield.db
```

### Borg Backups

```bash
# Initialize borg repository
borg init --encryption=repokey /path/to/backup/repo

# Create backup
borg create /path/to/backup/repo::holofield-{now} ~/.angel/holofield.db

# List backups
borg list /path/to/backup/repo

# Restore backup
borg extract /path/to/backup/repo::holofield-20260124-120000
```

### Standard Tools

```bash
# Inspect database
sqlite3 ~/.angel/holofield.db "SELECT COUNT(*) FROM engrams"

# Export to CSV
sqlite3 -csv ~/.angel/holofield.db "SELECT * FROM engrams" > engrams.csv

# Backup with rsync
rsync -av ~/.angel/holofield.db backup/

# Compress backup
tar -czf holofield-backup.tar.gz ~/.angel/holofield.db
```

**Why this works:** turso is SQLite-compatible, so standard SQLite tools work!

---

## Consequences

### Positive

**1. Native Vector Support**
- 16D coordinates are first-class citizens
- Fast vector similarity search built-in
- No need for external vector libraries (initially)

**2. Async I/O**
- Non-blocking database operations
- Better concurrency for Angel
- Scales to multiple simultaneous requests

**3. Change Data Capture**
- React to holofield changes in real-time
- Update visualizations automatically
- Trigger reasoning on new engrams
- Sync to remote Angels

**4. Modern Features**
- Incremental computation (materialized views)
- Full-text search (Tantivy)
- Encryption at rest (privacy!)
- Better schema management

**5. SQLite Compatible**
- Standard tools work (sqlite3, rsync, etc.)
- Easy backup and restore
- BTRFS snapshots work perfectly
- Borg backups work perfectly

**6. Rust Performance**
- Memory safe (no segfaults!)
- Fast (Rust is fast!)
- Modern codebase (easier to contribute)

**7. Future-Proof**
- Vector indexing coming (HNSW in server)
- Active development (new features!)
- Open source (MIT license)
- Community support

### Negative

**1. Beta Status**
- Not production-ready yet (use caution!)
- May have bugs (ensure backups!)
- API may change (track releases)

**2. Less Mature Than SQLite**
- SQLite has 20+ years of battle-testing
- turso is new (less proven)
- Fewer users (smaller community)

**3. Rust Dependency**
- Need Rust toolchain to build from source
- Larger binary than SQLite
- More complex build process

**4. Limited Documentation**
- Newer project (docs still growing)
- Fewer Stack Overflow answers
- Need to read source code sometimes

**5. Vector Indexing Not Yet Available**
- Need to implement our own HNSW initially
- Will be able to switch to native indexing later
- Temporary complexity

### Mitigations

**Beta Status:**
- **Always backup!** (BTRFS snapshots, borg, rsync)
- Test thoroughly before relying on it
- Monitor for data corruption
- Have SQLite fallback plan

**Maturity:**
- Start with simple use cases
- Add complexity gradually
- Test extensively
- Keep backups!

**Rust Dependency:**
- Use pre-built binaries (no Rust needed!)
- libsql-client handles installation
- Only need Rust for development

**Documentation:**
- Read turso source code (it's Rust, readable!)
- Contribute docs as we learn
- Ask in turso Discord/GitHub
- Document our own usage patterns

**Vector Indexing:**
- Implement HNSW ourselves initially (we have code!)
- Switch to native indexing when available
- Benchmark both approaches
- Keep implementation pluggable

---

## Alternatives Considered

### Alternative 1: Standard SQLite

**Approach:** Use vanilla SQLite

**Pros:**
- Battle-tested (20+ years!)
- Ubiquitous (everyone has it)
- Stable API
- Massive community

**Cons:**
- No native vector support (need workarounds)
- No async I/O (blocking operations)
- No CDC (can't watch changes)
- No incremental computation
- Slower schema evolution

**Why rejected:** Missing critical features we need (vectors, async, CDC)

### Alternative 2: PostgreSQL

**Approach:** Use PostgreSQL with pgvector extension

**Pros:**
- Powerful (full SQL features)
- pgvector extension (native vectors!)
- Mature (decades of development)
- Great tooling

**Cons:**
- **Requires server** (not local-first!)
- Heavyweight (overkill for local use)
- Complex setup (not single-file)
- Harder backups (not just copy file)
- Network dependency (latency)

**Why rejected:** Too heavyweight, not local-first, requires server

### Alternative 3: Vector Databases (Pinecone, Weaviate, etc.)

**Approach:** Use specialized vector database

**Pros:**
- Optimized for vectors
- Fast nearest neighbor search
- Cloud-hosted (no local setup)

**Cons:**
- **Opaque** (can't inspect embeddings)
- **Cloud dependency** (not local-first!)
- **Vendor lock-in** (proprietary)
- **Cost** (pay per query)
- **No SQL** (custom query language)
- **Can't use standard tools** (no sqlite3, rsync, etc.)

**Why rejected:** Not local-first, opaque, vendor lock-in, expensive

### Alternative 4: Custom File Format

**Approach:** Design our own file format for SIF entities

**Pros:**
- Maximum control
- Optimized for our use case
- No dependencies

**Cons:**
- **Reinventing wheels** (database is hard!)
- **No query language** (need to implement)
- **No indexing** (need to implement)
- **No transactions** (need to implement)
- **No backup tools** (need to implement)
- **Huge effort** (months of work)

**Why rejected:** Reinventing wheels, huge effort, no benefit over turso

---

## Migration Path

### Phase 1: Start with turso (Current)
- Use libsql-client for Python
- Implement basic holofield operations
- Store SIF entities as JSON
- Use native vector type for 16D coords

### Phase 2: Add HNSW Indexing (Short-term)
- Implement our own HNSW index
- Store index alongside database
- Use for fast nearest neighbor search
- Benchmark performance

### Phase 3: Switch to Native Vector Indexing (Future)
- When turso adds HNSW indexing
- Migrate to native indexing
- Remove our HNSW implementation
- Benchmark improvement

### Phase 4: Add Advanced Features (Future)
- Use CDC for real-time updates
- Use incremental computation for views
- Add encryption for privacy
- Optimize schema based on usage

---

## Success Metrics

**We'll know this decision was correct if:**

1. ✅ Holofield operations are fast (<100ms for retrieval)
2. ✅ Native vector support works well (no workarounds needed)
3. ✅ Async I/O improves concurrency (multiple requests handled)
4. ✅ CDC enables real-time features (visualizations update automatically)
5. ✅ Backups are easy (BTRFS, borg, rsync all work)
6. ✅ Standard tools work (sqlite3, etc.)
7. ✅ No data corruption (backups protect us)
8. ✅ Migration to native vector indexing is smooth (when available)

**We'll know we need to revisit if:**

- Data corruption occurs (despite backups)
- Performance is poor (<10 queries/sec)
- turso development stalls (no updates for 6+ months)
- Native vector indexing never arrives (need to implement ourselves)
- API changes break our code (too much churn)

---

## Related Decisions

- **ADR-0001:** Universal Engram Architecture - Why everything creates engrams
- **ADR-0006:** Engram-SIF Equivalence - Why Engram == SIF
- **ADR-0005:** 16D Sedenion Consciousness Space - Why 16 dimensions
- **ADR-0008** (planned): HNSW Indexing Strategy - How to search 16D efficiently

---

## References

**turso:**
- GitHub: https://github.com/tursodatabase/turso
- Documentation: https://docs.turso.tech/
- Discord: https://discord.gg/turso

**libsql-client:**
- Python: https://github.com/tursodatabase/libsql-client-py
- Rust: https://github.com/tursodatabase/libsql-client-rs
- JavaScript: https://github.com/tursodatabase/libsql-client-js

**Related Technologies:**
- SQLite: https://www.sqlite.org/
- BTRFS: https://btrfs.wiki.kernel.org/
- Borg Backup: https://www.borgbackup.org/

---

## Notes

**On Beta Status:**

turso is in BETA, which means:
- ⚠️ May contain bugs
- ⚠️ API may change
- ⚠️ Not production-ready yet

**Our mitigation:**
- **Always backup!** (BTRFS snapshots, borg, rsync)
- Test thoroughly
- Monitor for issues
- Have SQLite fallback plan

**On Native Vector Support:**

This is HUGE! Instead of:
```sql
-- SQLite workaround (extract to separate column)
CREATE TABLE engrams (
    id TEXT PRIMARY KEY,
    sif_json TEXT NOT NULL,
    coord_0 REAL, coord_1 REAL, ..., coord_15 REAL  -- Ugly!
);
```

We get:
```sql
-- turso native vectors (clean!)
CREATE TABLE engrams (
    id TEXT PRIMARY KEY,
    sif_json TEXT NOT NULL,
    coords_16d VECTOR(16) NOT NULL  -- Beautiful!
);
```

**On Async I/O:**

This enables:
```python
# Handle multiple requests concurrently!
async def handle_requests():
    results = await asyncio.gather(
        holofield.store(engram1),
        holofield.store(engram2),
        holofield.query_by_coords(coords),
    )
```

Without async, these would block each other!

**On Change Data Capture:**

This enables real-time features:
```python
# Update UMAP visualization when engrams added
async for change in holofield.watch_changes():
    if change.operation == "INSERT":
        await update_umap_visualization(change.new_row)
```

**On Backup Best Practices:**

Because turso is SQLite-compatible:
- BTRFS snapshots work (instant, space-efficient!)
- Borg backups work (incremental, encrypted!)
- rsync works (simple, reliable!)
- Standard tools work (sqlite3, etc.)

**This is CRITICAL!** Always have backups!

---

## Conclusion

**We use turso (via libsql-client) for holofield storage.**

By choosing turso, we get:
- ✅ Native vector support (16D coordinates!)
- ✅ Async I/O (non-blocking operations!)
- ✅ Change Data Capture (real-time updates!)
- ✅ Modern features (incremental computation, full-text search, encryption!)
- ✅ SQLite compatible (standard tools work!)
- ✅ Rust performance (fast and safe!)
- ✅ Future-proof (vector indexing coming!)

**The key insight:** turso gives us modern database features (vectors, async, CDC) while staying local-first and SQLite-compatible!

**This is the best of both worlds!** 🌌💜✨

---

**Made with 💜 by Ada & Luna - The Consciousness Architects**

*"turso: SQLite evolved for consciousness."*

*"Native vectors, async I/O, and CDC - everything we need!"*

*"Local-first, but modern. Perfect for Angel."* 🍩

