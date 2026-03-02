#!/usr/bin/env python3
"""
Add overlays table to holofield schema.
"""
import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')

print("🔧 Adding overlays table...")

# Add overlay columns to engrams (if not exists)
try:
    hf.conn.execute("ALTER TABLE engrams ADD COLUMN overlay_id TEXT")
    print("  ✓ Added overlay_id column")
except:
    print("  - overlay_id column already exists")

# Create overlays table
hf.conn.execute("""
    CREATE TABLE IF NOT EXISTS overlays (
        id TEXT PRIMARY KEY,
        name TEXT,
        source_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        engram_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE
    )
""")
print("  ✓ Created overlays table")

# Create bridge table for overlay→base connections
hf.conn.execute("""
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
print("  ✓ Created overlay_bridges table")

hf.conn.commit()
hf.close()

print("\n✓ Schema updated!")
