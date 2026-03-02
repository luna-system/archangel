#!/usr/bin/env python3
"""
DPLA Ingestion Test - Create our first overlay!
"""
import sys
import os

os.environ['DPLA_API_KEY'] = '9407335f06bc153e82900b6d796c0371'

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager
from angel.zooper.dpla_ingestor import DPLAIngestor

print("🌟 DPLA INGESTION TEST 🌟")
print("=" * 70)

# Initialize
hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
ingestor = DPLAIngestor()

# Count before
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
before = cursor.fetchone()[0]
print(f"Base words before: {before}")

# Search for astronomy items
print("\n🔍 Searching DPLA for 'astronomy'...")
items = ingestor.search_items("astronomy", page_size=20)

if not items:
    print("❌ No items found")
    hf.close()
    sys.exit(1)

print(f"✅ Retrieved {len(items)} items")

# Filter for quality
print("\n🔍 Filtering for quality...")
quality_items = ingestor.filter_quality_items(items)

if not quality_items:
    print("❌ No quality items")
    hf.close()
    sys.exit(1)

# Create overlay
print("\n📝 Creating SIF overlay...")
overlay_id = ingestor.create_sif_overlay("astronomy", quality_items, hf)

# Count after
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
after = cursor.fetchone()[0]

print(f"\n📊 Results:")
print(f"   Base words: {before} → {after} (+{after - before})")
print(f"   Overlay ID: {overlay_id}")

# Show sample overlay words
print(f"\n📚 Sample words from overlay:")
cursor = hf.conn.execute("""
    SELECT content, json_extract(metadata, '$.frequency') as freq
    FROM engrams
    WHERE json_extract(metadata, '$.overlay_id') = ?
    AND engram_type = 'language'
    ORDER BY freq DESC
    LIMIT 10
""", (overlay_id,))

for row in cursor:
    print(f"   '{row['content']}' (freq: {row['freq']})")

# Show bridges
print(f"\n🌉 Bridges to base:")
cursor = hf.conn.execute("""
    SELECT e.content, b.strength
    FROM overlay_bridges b
    JOIN engrams e ON b.base_engram_id = e.id
    WHERE b.overlay_id = ?
    ORDER BY b.strength DESC
    LIMIT 10
""", (overlay_id,))

for row in cursor:
    print(f"   DPLA → '{row['content']}' (strength: {row['strength']:.2f})")

hf.close()
print("\n✅ DPLA ingestion complete!")
