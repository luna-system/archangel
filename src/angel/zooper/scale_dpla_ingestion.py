#!/usr/bin/env python3
"""
Scale DPLA ingestion - Multiple topics, larger batches!
"""
import sys
import os

os.environ['DPLA_API_KEY'] = '9407335f06bc153e82900b6d796c0371'

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager
from angel.zooper.dpla_ingestor import DPLAIngestor

print("🌟 SCALING DPLA INGESTION 🌟")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
ingestor = DPLAIngestor()

# Count before
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
before = cursor.fetchone()[0]
cursor = hf.conn.execute("SELECT COUNT(*) FROM overlays WHERE is_active = TRUE")
before_overlays = cursor.fetchone()[0]

print(f"Starting: {before} words, {before_overlays} overlays")

# Multiple topics for diversity
topics = [
    ("astronomy", 50),        # Science
    ("shakespeare", 30),      # Literature  
    ("physics", 40),          # Science
    ("history", 40),          # Humanities
    ("poetry", 30),           # Arts
]

total_items = 0
total_engrams = 0
total_bridges = 0

for topic, limit in topics:
    print(f"\n{'='*70}")
    print(f"📚 Topic: {topic} (limit: {limit})")
    print("=" * 70)
    
    # Search
    items = ingestor.search_items(topic, page_size=limit)
    if not items:
        print(f"   ⚠ No items found for '{topic}'")
        continue
    
    # Filter
    quality = ingestor.filter_quality_items(items)
    if not quality:
        print(f"   ⚠ No quality items for '{topic}'")
        continue
    
    # Create overlay
    overlay_id = ingestor.create_sif_overlay(topic, quality, hf)
    
    # Count what we got
    cursor = hf.conn.execute(
        "SELECT COUNT(*) FROM engrams WHERE json_extract(metadata, '$.overlay_id') = ?",
        (overlay_id,)
    )
    engrams = cursor.fetchone()[0]
    
    cursor = hf.conn.execute(
        "SELECT COUNT(*) FROM overlay_bridges WHERE overlay_id = ?",
        (overlay_id,)
    )
    bridges = cursor.fetchone()[0]
    
    total_items += len(quality)
    total_engrams += engrams
    total_bridges += bridges
    
    print(f"   ✓ Added {engrams} engrams, {bridges} bridges")

# Final stats
print("\n" + "=" * 70)
print("📊 FINAL RESULTS")
print("=" * 70)

cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
after = cursor.fetchone()[0]

cursor = hf.conn.execute("SELECT COUNT(*) FROM overlays WHERE is_active = TRUE")
after_overlays = cursor.fetchone()[0]

print(f"\nWords: {before} → {after} (+{after - before})")
print(f"Overlays: {before_overlays} → {after_overlays} (+{after_overlays - before_overlays})")
print(f"Total items ingested: {total_items}")
print(f"Total engrams created: {total_engrams}")
print(f"Total bridges built: {total_bridges}")

# Show top new words
print(f"\n🔝 Top New Words by Frequency:")
cursor = hf.conn.execute("""
    SELECT content, json_extract(metadata, '$.frequency') as freq
    FROM engrams
    WHERE json_extract(metadata, '$.source') LIKE 'dpla%'
    ORDER BY freq DESC
    LIMIT 20
""")

for row in cursor:
    print(f"   '{row['content']}' (freq: {row['freq']})")

# Show all active overlays
print(f"\n📦 Active Overlays:")
cursor = hf.conn.execute(
    "SELECT name, engram_count FROM overlays WHERE is_active = TRUE ORDER BY created_at"
)
for row in cursor:
    print(f"   {row['name']}: {row['engram_count']} engrams")

hf.close()
print("\n✅ Scale-up complete!")
