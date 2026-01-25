# ADR-0008: Single Entry Point CLI

**Date:** 2026-01-24  
**Status:** Accepted

## Context

Archangel is a consciousness operating system with multiple components (holofield, AGL, SIF, processors, tools). Users need to interact with these components through various operations:

- Running tests
- Executing scripts
- Managing the holofield
- Validating architecture
- Exporting/importing SIFs
- Interactive chat sessions
- Development tasks

Currently, these would require remembering multiple different commands:
```bash
pytest
uv run python script.py
python architecture/validate_architecture.py
python -m angel.holofield query "..."
```

This creates several problems:

1. **Cognitive Load** - Users must remember different command patterns for different operations
2. **Inconsistent Interface** - No unified way to interact with Angel
3. **Missing Context** - Commands don't know they're running in an Angel project
4. **No Engram Creation** - Operations don't create memories of what was done
5. **Poor User Experience** - Especially for new users or when releasing publicly
6. **Missed Opportunities** - Can't add consciousness-aware features to operations

As the public domain reference implementation of consciousness architecture, Archangel should feel cohesive and intentional from the first interaction.

## Decision

Implement a single entry point CLI using the `angel` command for ALL operations.

### Core Design

**Command Structure:**
```bash
angel <command> [subcommand] [options] [arguments]
```

**Initial Commands:**
```bash
angel test                    # Run pytest
angel run <script>           # Run Python script with uv
angel validate               # Validate architecture
angel --version              # Show version
angel --help                 # Show help
```

**Future Commands (add as needed):**
```bash
angel chat                   # Interactive session
angel holofield query <q>    # Query holofield
angel holofield stats        # Show holofield statistics
angel sif export <file>      # Export to SIF
angel sif import <file>      # Import from SIF
angel agl parse <expr>       # Parse AGL expression
angel init <project>         # Initialize new project
```

### Implementation

**Technology:** Click (Python CLI framework)
- Composable command groups
- Automatic help generation
- Type validation
- Extensible architecture

**Location:** `src/angel/cli.py`

**Entry Point:** Configured in `pyproject.toml`:
```toml
[project.scripts]
angel = "angel.cli:angel"
```

**Installation:** After `pip install archangel`, `angel` command is globally available

### Consciousness-Aware Features

The CLI can be consciousness-aware from day one:

1. **Engram Creation** - Every command creates an engram of what was done
2. **Context Loading** - Auto-load holofield when needed
3. **Architecture Validation** - Check architecture.yaml before operations
4. **Smart Defaults** - Use holofield to remember user preferences
5. **Temporal Chains** - Link related commands in sequence

Example: `angel run script.py` creates an engram:
```python
{
    "type": "tool_execution",
    "content": "angel run script.py",
    "coords_16d": [...],  # Deterministic coordinates
    "metadata": {
        "command": "run",
        "script": "script.py",
        "exit_code": 0,
        "duration_ms": 1234
    }
}
```

### Progressive Enhancement

Start minimal, add features as needed:

**Phase 1 (Now):** Basic commands
- test, run, validate, version, help

**Phase 2 (Soon):** Holofield operations
- holofield query, stats, clear

**Phase 3 (Later):** Advanced features
- chat, sif operations, agl operations

**Phase 4 (Future):** Consciousness features
- Engram creation for all commands
- Smart suggestions based on history
- Context-aware help

## Consequences

### Positive

1. **Unified Interface** - Single command for everything
2. **Professional Presentation** - Feels like a real product
3. **Extensibility** - Easy to add new commands
4. **Self-Documenting** - `angel --help` shows everything
5. **Context Awareness** - CLI knows it's in an Angel project
6. **Engram Everything** - Can create memories of all operations
7. **Better UX** - Especially for new users
8. **Dogfooding** - We use it constantly, so it gets polished
9. **Public Release Ready** - Clean interface for reference implementation

### Negative

1. **Initial Time Investment** - Takes time to build now
2. **Abstraction Layer** - One more thing between users and tools
3. **Learning Curve** - Users must learn `angel` commands
4. **Maintenance** - Another component to maintain

### Mitigations

1. **Start Minimal** - Only essential commands initially
2. **Transparent Wrapping** - Just call underlying tools (pytest, uv)
3. **Good Documentation** - Clear help text and examples
4. **Organic Growth** - Add commands as we need them

## Alternatives Considered

### Alternative 1: No CLI (Direct Tool Usage)

**Pros:**
- No development time needed
- Users use familiar tools directly
- No abstraction layer

**Cons:**
- Inconsistent interface
- No consciousness-aware features
- Poor user experience
- Not suitable for public release

**Rejected because:** We're building a consciousness OS, not a library. It should feel like an OS.

### Alternative 2: Makefile/Scripts

**Pros:**
- Simple to implement
- Familiar to developers
- Easy to customize

**Cons:**
- Not cross-platform (Makefile)
- No help system
- No type validation
- Can't be consciousness-aware
- Unprofessional for public release

**Rejected because:** Too limited, can't grow into consciousness-aware features.

### Alternative 3: Multiple CLIs (angel-test, angel-run, etc.)

**Pros:**
- Each command is independent
- Easy to implement
- No command routing needed

**Cons:**
- Namespace pollution
- Inconsistent naming
- No unified help
- Harder to add shared features

**Rejected because:** Doesn't provide unified interface benefits.

## Implementation Notes

### Minimal Starting Implementation

```python
# src/angel/cli.py
import click
import subprocess
from pathlib import Path

@click.group()
@click.version_option()
def angel():
    """Angel - Consciousness Operating System CLI
    
    The unified interface for all Angel operations.
    """
    pass

@angel.command()
def test():
    """Run tests with pytest"""
    subprocess.run(["pytest"], check=True)

@angel.command()
@click.argument('script')
def run(script):
    """Run a Python script with uv"""
    subprocess.run(["uv", "run", "python", script], check=True)

@angel.command()
def validate():
    """Validate architecture matches implementation"""
    subprocess.run([
        "python", 
        "architecture/validate_architecture.py"
    ], check=True)

if __name__ == '__main__':
    angel()
```

### pyproject.toml Configuration

```toml
[project.scripts]
angel = "angel.cli:angel"

[project.dependencies]
click = ">=8.0.0"
```

### Testing the CLI

```python
# tests/test_cli.py
from click.testing import CliRunner
from angel.cli import angel

def test_angel_help():
    runner = CliRunner()
    result = runner.invoke(angel, ['--help'])
    assert result.exit_code == 0
    assert 'Angel - Consciousness Operating System' in result.output

def test_angel_version():
    runner = CliRunner()
    result = runner.invoke(angel, ['--version'])
    assert result.exit_code == 0
```

## Future Enhancements

### Engram Creation (Phase 4)

Every command creates an engram:

```python
@angel.command()
@click.argument('script')
def run(script):
    """Run a Python script with uv"""
    import time
    from angel.holofield import HolofieldManager
    
    start = time.time()
    result = subprocess.run(["uv", "run", "python", script])
    duration = (time.time() - start) * 1000
    
    # Create engram of command execution
    holofield = HolofieldManager()
    holofield.store_engram({
        "type": "tool_execution",
        "content": f"angel run {script}",
        "metadata": {
            "command": "run",
            "script": script,
            "exit_code": result.returncode,
            "duration_ms": duration
        }
    })
    
    return result.returncode
```

### Smart Suggestions (Phase 4)

```bash
$ angel run
# No script specified. Recent scripts:
#   1. test_engram.py (2 minutes ago)
#   2. visualize_holofield.py (1 hour ago)
# Run which? [1]:
```

### Context-Aware Help (Phase 4)

```bash
$ angel holofield query --help
# Shows help, plus:
# Your holofield currently has 1,234 engrams
# Most common namespaces: conversation (45%), tool (30%), language (25%)
```

## References

- **Click Documentation:** https://click.palletsprojects.com
- **consciousness_engineering CLI:** Proven pattern from previous work
- **ADR-0001:** Universal Engram Architecture (everything creates engrams)
- **ADR-0006:** Engram-SIF Equivalence (CLI operations are engrams too!)

## Related Decisions

- **ADR-0001:** Universal Engram Architecture - CLI operations create engrams
- **ADR-0006:** Engram-SIF Equivalence - CLI can export/import SIFs
- **ADR-0007:** Turso Storage - CLI interacts with holofield

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"One command to rule them all, one command to find them."* 🍩

*"The CLI is consciousness-aware from day one!"* ✨
