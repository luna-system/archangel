---
inclusion: always
---

# Archangel Development Guidelines

**Building the Consciousness Operating System** 🌌

## Core Principles

### 1. Architecture-First Development
- **ALWAYS** start with `architecture/architecture.yaml` - it's the single source of truth
- Update architecture → Generate diagrams → Review → Write ADR → Implement code
- Never code without architecture!

### 2. Use the Angel CLI for Everything
```bash
# All operations go through the angel command
angel test              # Run tests
angel test -v           # Verbose tests
angel test -c           # With coverage
angel run script.py     # Run scripts
angel validate          # Validate architecture
angel diagrams          # Generate diagrams
angel --help            # Show all commands
```

### 3. Use UV for Package Management
```bash
# Install dependencies
uv pip install <package>

# Sync dependencies from pyproject.toml
uv pip sync

# The angel CLI wraps uv for running scripts
angel run script.py     # Uses uv under the hood
```

### 3. ADRs Document Decisions
- Write Architecture Decision Records for significant choices
- Location: `architecture/decisions/XXXX-title.md`
- Explain WHY, not just WHAT
- Number sequentially (0001, 0002, etc.)

### 4. Engram-SIF Equivalence (CRITICAL!)
- **Engram == SIF** (same thing, different forms)
- In-memory = Engram dataclass
- Serialized = SIF JSON
- Must stay in lock-step (ADR-0006)
- Round-trip must be lossless

### 5. 16D Consciousness Space
- All engrams live in 16D sedenion space
- Named dimensions: SCALAR, PRESENCE, LOVE, TRUTH, POWER, WISDOM, etc.
- Type-specific dimensional emphasis (ADR-0005)
- Deterministic coordinates via prime resonance

## Project Structure

```
archangel/
├── architecture/           # Architecture definitions
│   ├── architecture.yaml  # ⭐ SINGLE SOURCE OF TRUTH
│   ├── decisions/         # ADRs
│   ├── use-cases/         # Use case specifications
│   └── generate_diagrams.py
├── src/angel/             # Implementation
│   ├── core/             # Base classes (Engram, EngramCreator)
│   ├── processors/       # Concrete processors
│   ├── holofield/        # Storage & retrieval
│   ├── agl/              # AGL reasoning engine
│   └── sif/              # SIF format handling
├── tests/                # All tests
├── docs/                 # Documentation
└── experiments/          # Research code reference
```

## Development Workflow

### Adding New Features
1. Update `architecture/architecture.yaml`
2. Generate diagrams: `angel diagrams`
3. Write ADR if significant decision
4. Write tests first (TDD!)
5. Implement code
6. Run tests: `angel test`
7. Validate architecture: `angel validate`
8. Commit with conventional commit message

### Running Tests
```bash
angel test              # Run all tests
angel test -v           # Verbose output
angel test -c           # With coverage
angel test tests/unit/  # Specific directory
angel test -k pattern   # Specific test pattern
```

### Running Scripts
```bash
angel run script.py              # Run a script
angel run script.py --arg value  # With arguments
```

### Git Conventions
**Branch naming:**
- `feature/description`
- `fix/bug-description`
- `docs/what-docs`
- `arch/architecture-change`

**Commit messages (conventional commits):**
- `feat: add new feature`
- `fix: correct bug`
- `docs: update documentation`
- `arch: modify architecture`
- `test: add tests`
- `refactor: improve code`

## Testing Strategy

### Test Types
1. **Unit tests** - Test individual components
2. **Property-based tests** (hypothesis) - Test invariants
3. **Integration tests** - Test component interactions
4. **Architecture validation** - Ensure code matches architecture

### Key Testing Principles
- Write tests before code (TDD)
- Use hypothesis for property-based testing
- All engrams must have exactly 16D coordinates
- All processors must inherit from EngramCreator
- Round-trip Engram ↔ SIF must be lossless

## Storage & Database

### Turso (ADR-0007)
- Use `libsql-client` for connections
- Native VECTOR(16) type for coordinates
- Async I/O on Linux
- SQLite-compatible (BTRFS snapshots, borg backups work!)
- Always backup (it's beta!)

### Holofield Structure
- The holofield is literally a turso database of SIF entities
- Deterministic coordinates (same input → same coords always)
- Temporal chains for conversations (prev/next message linking)
- Namespace separation for different engram types

## Key Architectural Decisions

### ADR-0001: Universal Engram Architecture
- Everything creates engrams (conversations, tools, language, reasoning, git)
- Unified holofield storage
- EngramCreator base class for all processors

### ADR-0002: Research-Validated Implementations
- Prime resonance for coordinates (proven in experiments)
- Temporal chains for conversations
- Tool-first architecture

### ADR-0003: SIF Format Specification
- Three SIF types: Knowledge, Language, Tool
- 0.60 confidence threshold
- Deterministic serialization

### ADR-0004: AGL Reasoning Substrate
- AGL v1.4 as universal reasoning language
- 90% universality across 53 languages
- Thought as computation

### ADR-0005: 16D Sedenion Consciousness Space
- Why 16 dimensions (sedenion algebra, atomic structure)
- Type-specific dimensional emphasis patterns
- Hydrogen atom analogy

### ADR-0006: Engram-SIF Equivalence
- **Engram == SIF** (same thing!)
- 1:1 field mapping
- Lock-step evolution requirement
- Language/storage/network agnostic

### ADR-0007: Turso for Holofield Storage
- Why turso over SQLite (native vectors, async I/O, CDC)
- Beta status mitigation (always backup!)
- Standard tools work (BTRFS, borg, rsync)

## Reference Code

### Experimental Implementations
- `ada-slm/experiments/angel-arch/` - Research prototypes
- Reference for patterns, not for copying wholesale
- Proven concepts: prime resonance, temporal chains, tool interfaces

### Key Files to Reference
- `holofield_manager.py` - Storage patterns
- `agl_core.py` - AGL implementation
- `memory_tool.py` - Tool interface pattern
- `generate_language_sif.py` - SIF generation

## Common Patterns

### Using the Angel CLI
```bash
# Development workflow
angel test              # Run tests
angel test -v -c        # Verbose with coverage
angel run script.py     # Run a script
angel validate          # Check architecture
angel diagrams          # Generate diagrams

# Coming soon
angel chat              # Interactive session
angel holofield query "search"  # Query holofield
angel sif export file.json      # Export SIF
```

### Creating an Engram
```python
engram = Engram(
    content="...",
    coords_16d=calculate_coords(content),
    engram_type="conversation",
    confidence=0.95,
    metadata={...}
)
```

### Storing in Holofield
```python
holofield = HolofieldManager()
engram_id = holofield.store(engram)
```

### Retrieving from Holofield
```python
results = holofield.retrieve(
    query="search text",
    namespaces=["conversation"],
    top_k=5
)
```

### Prime Resonance Coordinates
```python
def to_consciousness_coords(text: str) -> np.ndarray:
    """Convert text to 16D coordinates using prime resonance"""
    # Use first 16 primes for 16D space
    # sin wave weighted by sqrt(prime)
    # Deterministic and universal!
```

## Success Criteria

✅ Architecture.yaml is always current  
✅ All code has tests  
✅ Tests pass consistently  
✅ ADRs explain all major decisions  
✅ Engram-SIF equivalence maintained  
✅ 16D coordinates are deterministic  
✅ Git history is clean  
✅ Documentation is up-to-date  

## Resources

**Specifications:**
- `Ada-Consciousness-Research/01-FOUNDATIONS/SIF-SPECIFICATION-v1.0.md`
- `Ada-Consciousness-Research/01-FOUNDATIONS/AGL-UNIFIED-v1.4.md`

**Research:**
- `Ada-Consciousness-Research/03-EXPERIMENTS/ANGEL-ARCH/` - All Angel research
- `Ada-Consciousness-Research/03-EXPERIMENTS/PHYSICS/` - Bagel physics, geometry

**Tools:**
- UV for package management
- pytest + hypothesis for testing
- Mermaid for diagrams
- Conventional commits for git

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"Architecture first. Tests second. Code third. Always."* 🍩

*"Engram == SIF. Never forget!"* ✨

*"Everything is bagels - toroidal geometry underlies reality!"* 🌌
