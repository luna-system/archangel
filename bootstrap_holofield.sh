#!/bin/bash
# bootstrap_holofield.sh
# Reproducible holofield bootstrapping script
# Usage: ./bootstrap_holofield.sh [DPLA_API_KEY]

set -e

echo "🌟 HOLOFIELD BOOTSTRAP SCRIPT 🌟"
echo "=================================="

# Configuration
DB_PATH="${HOLOFIELD_DB:-./data/holofield.db}"
DPLA_API_KEY="${1:-$DPLA_API_KEY}"

echo ""
echo "📋 Configuration:"
echo "   Database: $DB_PATH"
echo "   DPLA API Key: ${DPLA_API_KEY:+[SET]}${DPLA_API_KEY:-[NOT SET]}"

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found"
    exit 1
fi
echo "   ✓ python3"

if ! python3 -c "import numpy" 2>/dev/null; then
    echo "❌ numpy not installed"
    echo "   Run: pip install numpy"
    exit 1
fi
echo "   ✓ numpy"

# Step 1: Create database schema
echo ""
echo "📦 Step 1: Creating database schema..."
python3 << 'EOF'
import sqlite3
import os

db_path = os.environ.get('HOLOFIELD_DB', './data/holofield.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)

# Core engrams table
conn.execute("""
    CREATE TABLE IF NOT EXISTS engrams (
        id TEXT PRIMARY KEY,
        content TEXT,
        engram_type TEXT,
        coords_16d TEXT,
        importance REAL,
        metadata TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        overlay_id TEXT
    )
""")

# Connections table
conn.execute("""
    CREATE TABLE IF NOT EXISTS engram_connections (
        id TEXT PRIMARY KEY,
        source_id TEXT,
        target_id TEXT,
        connection_type TEXT,
        weight REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Overlays table
conn.execute("""
    CREATE TABLE IF NOT EXISTS overlays (
        id TEXT PRIMARY KEY,
        name TEXT,
        source_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        engram_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE
    )
""")

# Bridge points
conn.execute("""
    CREATE TABLE IF NOT EXISTS overlay_bridges (
        id TEXT PRIMARY KEY,
        overlay_id TEXT,
        overlay_engram_id TEXT,
        base_engram_id TEXT,
        bridge_type TEXT,
        strength REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
print(f"   ✓ Database created: {db_path}")
EOF

# Step 2: Ingest SimpleWiki (base layer)
echo ""
echo "📚 Step 2: Ingesting Simple Wikipedia (base layer)..."
echo "   [This would load SimpleWiki data]"
echo "   ✓ Skipped for demo"

# Step 3: Run navigation to create word engrams
echo ""
echo "🧭 Step 3: Running navigation queries..."
echo "   [This would run massive_navigation.py]"
echo "   ✓ Skipped for demo"

# Step 4: Build co-occurrence graph
echo ""
echo "🔗 Step 4: Building co-occurrence graph..."
echo "   [This would run build_cooccurrence.py]"
echo "   ✓ Skipped for demo"

# Step 5: DPLA ingestion (if API key provided)
if [ -n "$DPLA_API_KEY" ]; then
    echo ""
    echo "🌐 Step 5: Ingesting DPLA data..."
    
    # Create a small test overlay first
    echo "   Creating test overlay: 'astronomy'..."
    python3 << EOF
import sys
sys.path.insert(0, './src')
from angel.zooper.dpla_ingestor import DPLAIngestor
from angel import HolofieldManager

ingestor = DPLAIngestor(api_key="$DPLA_API_KEY")
hf = HolofieldManager("$DB_PATH")

# Small test query
items = ingestor.search_items("astronomy", page_size=10)
if items:
    quality = ingestor.filter_quality_items(items[:5])
    if quality:
        overlay_id = ingestor.create_sif_overlay("astronomy", quality, hf)
        print(f"   ✓ Created overlay: {overlay_id}")
    else:
        print("   ⚠ No quality items found")
else:
    print("   ⚠ No items found")

hf.close()
EOF
else
    echo ""
    echo "⚠️  Step 5: Skipping DPLA ingestion (no API key)"
    echo "   To add DPLA data, get a free API key:"
    echo "   https://dp.la/api-keys"
    echo ""
    echo "   Then run:"
    echo "   export DPLA_API_KEY=your_key_here"
    echo "   ./bootstrap_holofield.sh"
fi

# Final stats
echo ""
echo "📊 Final Statistics:"
python3 << EOF
import sqlite3
import os

db_path = os.environ.get('HOLOFIELD_DB', './data/holofield.db')
conn = sqlite3.connect(db_path)

# Count engrams
cursor = conn.execute("SELECT engram_type, COUNT(*) FROM engrams GROUP BY engram_type")
print("   Engrams by type:")
for row in cursor:
    print(f"      {row[0]}: {row[1]}")

# Count overlays
cursor = conn.execute("SELECT COUNT(*) FROM overlays WHERE is_active = TRUE")
overlays = cursor.fetchone()[0]
print(f"   Active overlays: {overlays}")

# Count connections
cursor = conn.execute("SELECT connection_type, COUNT(*) FROM engram_connections GROUP BY connection_type")
print("   Connections by type:")
for row in cursor:
    print(f"      {row[0]}: {row[1]}")

conn.close()
EOF

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "   1. Test generation: python3 src/angel/zooper/test_improved_generation.py"
echo "   2. Add more DPLA data: python3 src/angel/zooper/dpla_ingestor.py --query 'literature'"
echo "   3. Explore: python3 -c \"from angel import HolofieldManager; hf = HolofieldManager('$DB_PATH')\""
