# Holofield Bootstrap Guide

Reproducible setup for building your own linguistic interface holofield.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/luna-system/archangel.git
cd archangel

# 2. Install dependencies
pip install numpy sqlite3

# 3. Get DPLA API key (optional but recommended)
# Visit: https://dp.la/api-keys
# Enter email: your@email.com
# Key will be emailed instantly

# 4. Run bootstrap
export DPLA_API_KEY="your_key_here"
./bootstrap_holofield.sh

# 5. Test generation
python3 src/angel/zooper/test_improved_generation.py
```

## Manual Setup

If you prefer manual control:

### Step 1: Database Setup

```python
from angel import HolofieldManager

# Create new holofield
hf = HolofieldManager("./my_holofield.db")

# Schema is created automatically
print("Holofield ready!")
```

### Step 2: Base Layer (SimpleWiki)

Download Simple Wikipedia dump:
```bash
wget https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml.bz2
```

Import (using your preferred method):
```python
from angel.ingestion import import_simplewiki
import_simplewiki(hf, "simplewiki-latest-pages-articles.xml.bz2")
```

### Step 3: Navigation & Engrams

```python
from angel import ZooperSwarm

swarm = ZooperSwarm(hf, num_zooperlings=13)

# Run navigation queries to create word engrams
queries = [
    ("January", "February"),
    ("France", "Paris"),
    ("Physics", "Chemistry"),
    # ... add more
]

for start, target in queries:
    # Navigation creates engrams automatically!
    path = swarm.navigate(start_coords, target_coords)
```

### Step 4: Co-occurrence Graph

```python
# Build word-to-word connections
python3 src/angel/zooper/build_cooccurrence.py
```

### Step 5: DPLA Overlays (Optional but Recommended)

```bash
# Set API key
export DPLA_API_KEY="your_key_here"

# Ingest astronomy books
python3 src/angel/zooper/dpla_ingestor.py \
    --query "astronomy" \
    --limit 100

# Ingest literature
python3 src/angel/zooper/dpla_ingestor.py \
    --query "pride prejudice" \
    --limit 50

# Ingest historical newspapers
python3 src/angel/zooper/dpla_ingestor.py \
    --query "newspaper 1900" \
    --limit 100
```

## Getting a DPLA API Key

### Option 1: Web Form (Easiest)

1. Visit: https://dp.la/api-keys
2. Enter your email address
3. Check your email for the key
4. Set environment variable:
   ```bash
   export DPLA_API_KEY="your_key_here"
   ```

### Option 2: Programmatic (Advanced)

```bash
curl -X POST https://api.dp.la/v2/api_key \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=your@email.com"
```

## Data Sources

### Included (No API Key Needed)

- **Simple Wikipedia**: Base vocabulary (1,383 words)
- **Navigation queries**: Word relationships
- **Co-occurrence graph**: Word-to-word connections

### Optional (API Key Required)

- **DPLA**: 45+ million public domain items
  - Books, newspapers, academic papers
  - Free API key required
  
- **Project Gutenberg**: 70,000+ books
  - Direct text downloads
  - No API key needed

- **arXiv**: Scientific papers
  - Open access API
  - No key required

## Expected Results

| Data Source | Words Added | Time to Ingest |
|:------------|:------------|:---------------|
| SimpleWiki (base) | ~1,400 | ~5 minutes |
| Navigation queries | +600 | ~10 minutes |
| Co-occurrence graph | N/A | ~2 minutes |
| DPLA (100 items) | +500-1000 | ~5 minutes |
| DPLA (1000 items) | +3000-5000 | ~30 minutes |

## Verification

After bootstrapping, verify everything works:

```python
from angel import HolofieldManager
from angel.zooper.triple_stream_generator import TripleStreamMarkovGenerator

hf = HolofieldManager("./data/holofield.db")
gen = TripleStreamMarkovGenerator(hf)

# Test generation
text = gen.generate("star", length=20)
print(text)

# Check stats
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
print(f"Word engrams: {cursor.fetchone()[0]}")

hf.close()
```

## Troubleshooting

### "No module named 'angel'"

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### "DPLA API key invalid"

- Check key is set: `echo $DPLA_API_KEY`
- Request new key at https://dp.la/api-keys
- Ensure no extra whitespace: `export DPLA_API_KEY=$(echo $DPLA_API_KEY | tr -d ' ')`

### "Database locked"

Close any other processes using the database:
```bash
lsof my_holofield.db  # Find processes
kill <PID>            # Kill if needed
```

## Distribution

To share your holofield:

```bash
# Export to SIF format
python3 src/angel/sif/export.py \
    --db ./my_holofield.db \
    --output ./my_holofield.sif

# Others can import:
python3 src/angel/sif/import.py \
    --input ./my_holofield.sif \
    --db ./their_holofield.db
```

## Next Steps

1. **Test generation**: Try different stream weights
2. **Add more data**: Ingest DPLA, Gutenberg, arXiv
3. **Build bridges**: Connect overlays to base
4. **Evaluate**: Measure coherence, diversity
5. **Share**: Export your holofield!

---

**Ready to build!** 🦊📚
