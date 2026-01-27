# ADR-0015: Programmatic Machine Documentation

**Status:** Accepted  
**Date:** 2026-01-27  
**Authors:** Ada & Luna  
**Context:** Zooper RC1 development, AI-assisted coding workflow

---

## Context

When building Archangel with AI assistance, we need quick access to the codebase API without constantly jumping between files. The architecture is growing:

- **EngramCreator** abstract base class
- **HolofieldManager** storage layer
- **Multiple processors** (Tool, Memory, Reasoning, Zooper)
- **Data structures** (Engram, EngramConnection, etc.)
- **16D consciousness space** utilities

**The Problem:**
- AI needs to know the API to write correct code
- Jumping between files breaks flow
- Documentation gets stale quickly
- Need both machine-readable (AI context) and human-readable (browsing) formats

**The Vision:**
- Generate documentation programmatically from code
- Keep it always up-to-date
- Inject into AI context via steering
- Provide HTML docs for humans
- Future: Beautiful Sphinx documentation site

---

## Decision

**We implement dual-format programmatic documentation:**

### 1. AST-Based Codemap (Machine-Readable)

**Purpose:** AI context injection via steering

**Format:** Markdown codemap with:
- All classes and inheritance
- All methods with signatures and types
- Key docstrings
- Organized by module
- Lightweight and fast

**Output:** `.ai/archangel-codemap.md`

**Usage:** Steering rule injects when working on Archangel code

**Example:**
```markdown
# Archangel Codemap

## archangel.core.engram_creator

### EngramCreator (ABC)
Base class for anything that creates engrams.

**Constructor:**
- `holofield_manager: HolofieldManager`

**Abstract Methods:**
- `process(input_data: Any) -> Tuple[Any, Engram]`
- `to_16d(data: Any) -> np.ndarray[16]`

**Concrete Methods:**
- `create_engram(content: str, data: Any, ...) -> Engram`
- `store_engram(engram: Engram) -> str`

### ZooperSwarm (EngramCreator)
Attention mechanism via zooperling swarm.

**Inherits:** EngramCreator

**Constructor:**
- `holofield_manager: HolofieldManager`
- `num_zooperlings: int = 13`
- `eve_fleet: Optional[EVEFleet] = None`

**Methods:**
- `process(article_data: dict) -> Tuple[dict, Engram]`
- `parallel_decompose(article_data: dict) -> dict`
- `navigate(start_coords, target_coords, max_hops=5) -> List[str]`
```

### 2. Pydoc HTML Documentation (Human-Readable)

**Purpose:** Browsable API documentation

**Format:** Standard Python HTML docs

**Output:** `docs/api/` directory

**Usage:** Open in browser, search, navigate

**Future:** Integrate with Sphinx for professional docs site

---

## Implementation Strategy

### Phase 1: AST Codemap Generator (Immediate)

Create `archangel/scripts/generate_codemap.py`:

```python
"""
Generate markdown codemap from Python AST.

Extracts:
- Classes and inheritance
- Method signatures with types
- Docstrings (first line only)
- Organized by module

Output: .ai/archangel-codemap.md
"""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any

def parse_module(module_path: Path) -> Dict[str, Any]:
    """Parse Python module and extract structure"""
    with open(module_path) as f:
        tree = ast.parse(f.read())
    
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(parse_class(node))
    
    return {
        'module': module_path.stem,
        'classes': classes
    }

def parse_class(node: ast.ClassDef) -> Dict[str, Any]:
    """Extract class info from AST node"""
    return {
        'name': node.name,
        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
        'docstring': ast.get_docstring(node),
        'methods': [parse_method(m) for m in node.body if isinstance(m, ast.FunctionDef)]
    }

def parse_method(node: ast.FunctionDef) -> Dict[str, Any]:
    """Extract method signature"""
    args = [arg.arg for arg in node.args.args]
    returns = ast.unparse(node.returns) if node.returns else None
    
    return {
        'name': node.name,
        'args': args,
        'returns': returns,
        'docstring': ast.get_docstring(node)
    }

def generate_codemap(src_dir: Path, output_path: Path):
    """Generate markdown codemap"""
    modules = []
    for py_file in src_dir.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        modules.append(parse_module(py_file))
    
    # Generate markdown
    markdown = generate_markdown(modules)
    
    output_path.write_text(markdown)
    print(f"✨ Codemap generated: {output_path}")

def generate_markdown(modules: List[Dict]) -> str:
    """Convert parsed modules to markdown"""
    lines = ["# Archangel Codemap", ""]
    
    for module in modules:
        lines.append(f"## {module['module']}")
        lines.append("")
        
        for cls in module['classes']:
            lines.append(f"### {cls['name']}")
            if cls['bases']:
                lines.append(f"**Inherits:** {', '.join(cls['bases'])}")
            if cls['docstring']:
                lines.append(f"{cls['docstring'].split('.')[0]}.")
            lines.append("")
            
            for method in cls['methods']:
                args_str = ', '.join(method['args'])
                ret_str = f" -> {method['returns']}" if method['returns'] else ""
                lines.append(f"- `{method['name']}({args_str}){ret_str}`")
                if method['docstring']:
                    lines.append(f"  - {method['docstring'].split('.')[0]}.")
            lines.append("")
    
    return '\n'.join(lines)

if __name__ == "__main__":
    src_dir = Path("archangel/src")
    output_path = Path(".ai/archangel-codemap.md")
    generate_codemap(src_dir, output_path)
```

**Run regularly:**
```bash
python archangel/scripts/generate_codemap.py
```

### Phase 2: Pydoc HTML Generation (Immediate)

Add to `archangel/scripts/generate_docs.sh`:

```bash
#!/bin/bash
# Generate HTML documentation with pydoc

echo "📚 Generating Archangel API documentation..."

# Create docs directory
mkdir -p docs/api

# Generate HTML for each module
cd archangel/src
for module in $(find . -name "*.py" | grep -v __pycache__ | sed 's/\.\///g' | sed 's/\.py//g' | sed 's/\//./g'); do
    echo "  Documenting: $module"
    python -m pydoc -w $module
done

# Move HTML files to docs
mv *.html ../../docs/api/

echo "✨ Documentation generated in docs/api/"
echo "   Open docs/api/index.html to browse"
```

**Run regularly:**
```bash
bash archangel/scripts/generate_docs.sh
```

### Phase 3: Steering Integration (Immediate)

Create `.ai/steering/archangel-api.md`:

```markdown
---
inclusion: manual
context_key: archangel-api
---

# Archangel API Reference

When working on Archangel code, use this API reference.

**Auto-generated from code - DO NOT EDIT MANUALLY**

Last updated: 2026-01-27

---

#[[file:.ai/archangel-codemap.md]]
```

**Usage:** AI gets codemap injected when `#archangel-api` is in context

### Phase 4: Sphinx Integration (Future)

When ready for professional docs:

1. Install Sphinx: `pip install sphinx sphinx-rtd-theme`
2. Initialize: `sphinx-quickstart docs/`
3. Configure `docs/conf.py` to use pydoc output
4. Build: `make html`
5. Deploy to GitHub Pages or ReadTheDocs

---

## Advantages

### For AI-Assisted Development

✅ **Always up-to-date** - Generated from code, never stale
✅ **Fast context** - Markdown codemap loads instantly
✅ **No file jumping** - API at fingertips via steering
✅ **Type-aware** - Knows signatures and return types
✅ **Inheritance-aware** - Sees class hierarchies

### For Human Developers

✅ **Browsable HTML** - Standard pydoc format
✅ **Searchable** - Find classes/methods quickly
✅ **Familiar** - Standard Python documentation
✅ **Future-proof** - Easy Sphinx migration

### For Project Health

✅ **Documentation as code** - Single source of truth
✅ **CI/CD ready** - Generate on every commit
✅ **Version-tracked** - Docs match code version
✅ **Low maintenance** - Automated generation

---

## Workflow Integration

### Daily Development

1. Write code with docstrings
2. Run `generate_codemap.py` (or on save hook)
3. AI gets updated API via steering
4. Continue coding with fresh context

### Before Commits

```bash
# Update documentation
python archangel/scripts/generate_codemap.py
bash archangel/scripts/generate_docs.sh

# Commit with docs
git add .ai/archangel-codemap.md docs/api/
git commit -m "feat: add zooper swarm + update docs"
```

### CI/CD Pipeline (Future)

```yaml
# .github/workflows/docs.yml
name: Generate Documentation

on: [push]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate codemap
        run: python archangel/scripts/generate_codemap.py
      - name: Generate HTML docs
        run: bash archangel/scripts/generate_docs.sh
      - name: Commit docs
        run: |
          git add .ai/archangel-codemap.md docs/api/
          git commit -m "docs: auto-update API documentation"
          git push
```

---

## File Structure

```
archangel/
├── scripts/
│   ├── generate_codemap.py      # AST → Markdown
│   └── generate_docs.sh          # Pydoc → HTML
├── src/
│   └── archangel/
│       ├── core/
│       │   ├── engram_creator.py
│       │   └── holofield_manager.py
│       └── processors/
│           └── zooper_swarm.py
└── docs/
    └── api/                      # Generated HTML docs

.ai/
├── archangel-codemap.md          # Generated codemap
└── steering/
    └── archangel-api.md          # Steering rule
```

---

## Maintenance

### Update Frequency

- **Codemap:** After every significant code change
- **HTML docs:** Before commits, weekly, or on-demand
- **Sphinx:** When ready for public release

### Automation Options

1. **Git hooks:** Pre-commit hook runs generators
2. **File watchers:** Auto-regenerate on save
3. **CI/CD:** Generate on every push
4. **Manual:** Run scripts as needed

**Recommendation:** Start manual, add automation as needed

---

## Future Enhancements

### 1. Interactive Codemap

Generate interactive HTML codemap with:
- Collapsible sections
- Search functionality
- Cross-references
- Syntax highlighting

### 2. API Diff Tracking

Track API changes between versions:
```bash
python scripts/api_diff.py v1.0.0 v1.1.0
```

Output:
```
Added:
  - ZooperSwarm.navigate()
  - HebbianEdgeWeights class

Changed:
  - EngramCreator.process() signature

Removed:
  - (none)
```

### 3. Usage Examples

Extract examples from tests:
```python
# In test file
def test_zooper_decomposition():
    """
    Example: Decompose Wikipedia article
    
    >>> swarm = ZooperSwarm(holofield_manager)
    >>> results, engram = swarm.process(article_data)
    >>> print(len(results[1]))  # Word count
    28
    """
```

Include in generated docs!

### 4. Dependency Graph

Visualize class relationships:
```
EngramCreator (ABC)
├── ToolProcessor
├── MemoryProcessor
├── ReasoningProcessor
└── ZooperSwarm
    ├── Zooperling (13x)
    ├── EVEFleet
    └── HebbianEdgeWeights
```

---

## Consequences

### Positive

✅ **Faster development** - API always at hand
✅ **Better code quality** - Encourages good docstrings
✅ **Easier onboarding** - New developers have docs
✅ **AI-friendly** - Perfect for AI-assisted coding
✅ **Future-proof** - Easy to extend and improve

### Negative

⚠️ **Initial setup** - Need to write generators
⚠️ **Maintenance** - Must run regularly
⚠️ **Docstring discipline** - Only works if code is documented

### Mitigations

1. **Make it easy** - Simple scripts, clear workflow
2. **Automate** - Git hooks or CI/CD
3. **Lead by example** - Document core classes well

---

## Alternatives Considered

### Alternative 1: Manual Documentation

**Rejected:** Gets stale immediately, high maintenance

### Alternative 2: Sphinx Only

**Rejected:** Overkill for now, harder to inject into AI context

### Alternative 3: Just Comments

**Rejected:** Not machine-readable, can't generate docs

### Alternative 4: External Tools (Doxygen, etc.)

**Rejected:** Python-native tools are simpler and better

---

## Related ADRs

- **ADR-0001:** Universal Engram Architecture (what we're documenting!)
- **ADR-0013:** Zooper Swarm Architecture (first use case!)

---

## References

- Python AST module: https://docs.python.org/3/library/ast.html
- Pydoc: https://docs.python.org/3/library/pydoc.html
- Sphinx: https://www.sphinx-doc.org/

---

**Decision:** Accepted  
**Rationale:** Dual-format documentation (AST codemap + pydoc HTML) provides both machine-readable AI context and human-browsable docs. Low maintenance, always up-to-date, future-proof with Sphinx migration path.

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"Documentation that never gets stale!"* 📚✨  
*"AI-friendly and human-friendly!"* 🤖💜  
*"Code is the single source of truth!"* 🌌
