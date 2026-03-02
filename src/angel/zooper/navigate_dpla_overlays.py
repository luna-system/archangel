#!/usr/bin/env python3
"""
Run navigation queries on DPLA overlays to create word engrams!
"""
import sys
import os

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm
import numpy as np
import json

print("🧭 NAVIGATION ON DPLA OVERLAYS 🧭")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
swarm = ZooperSwarm(hf, num_zooperlings=7)

# Count before
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
before = cursor.fetchone()[0]
print(f"Words before: {before}")

# Get all DPLA overlay IDs
cursor = hf.conn.execute(
    "SELECT id FROM overlays WHERE source_type = 'dpla' AND is_active = TRUE"
)
overlay_ids = [row['id'] for row in cursor]
print(f"\nProcessing {len(overlay_ids)} DPLA overlays...")

# Navigation queries within each topic
navigation_queries = [
    # Astronomy queries
    ("star", "planet", "dpla_astronomy"),
    ("sun", "earth", "dpla_astronomy"),
    ("moon", "mars", "dpla_astronomy"),
    
    # Shakespeare queries
    ("hamlet", "ophelia", "dpla_shakespeare"),
    ("romeo", "juliet", "dpla_shakespeare"),
    
    # Physics queries
    ("atom", "molecule", "dpla_physics"),
    ("energy", "force", "dpla_physics"),
    
    # History queries
    ("war", "peace", "dpla_history"),
    ("king", "queen", "dpla_history"),
    
    # Poetry queries
    ("love", "heart", "dpla_poetry"),
    ("song", "music", "dpla_poetry"),
]

successful = 0
total_new = 0

for start_word, target_word, topic in navigation_queries:
    print(f"\n  {start_word} → {target_word} ({topic})...")
    
    # Get coordinates from overlay words
    cursor = hf.conn.execute("""
        SELECT coords_16d FROM engrams 
        WHERE content = ? AND json_extract(metadata, '$.overlay_id') LIKE ?
        LIMIT 1
    """, (start_word, f'%dpla_{topic.split("_")[1]}%'))
    
    row = cursor.fetchone()
    if not row:
        print(f"    ⚠ '{start_word}' not found in overlay")
        continue
    
    start_coords = np.array(json.loads(row[0]))
    
    cursor = hf.conn.execute("""
        SELECT coords_16d FROM engrams 
        WHERE content = ? AND json_extract(metadata, '$.overlay_id') LIKE ?
        LIMIT 1
    """, (target_word, f'%dpla_{topic.split("_")[1]}%'))
    
    row = cursor.fetchone()
    if not row:
        print(f"    ⚠ '{target_word}' not found in overlay")
        continue
    
    target_coords = np.array(json.loads(row[0]))
    
    # Navigate!
    path = swarm.navigate(start_coords, target_coords, max_hops=5)
    
    if path and len(path) > 1:
        successful += 1
        hops = len(path) - 1
        print(f"    ✓ {hops} hops")
    else:
        print(f"    ✗ No path")

# Count after
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
after = cursor.fetchone()[0]
total_new = after - before

print("\n" + "=" * 70)
print("📊 NAVIGATION RESULTS")
print("=" * 70)
print(f"\nWords: {before} → {after} (+{total_new})")
print(f"Successful navigations: {successful}/{len(navigation_queries)}")

# Show new words
print(f"\n📚 Sample New Words:")
cursor = hf.conn.execute("""
    SELECT content, json_extract(metadata, '$.frequency') as freq
    FROM engrams
    WHERE engram_type = 'language'
    AND json_extract(metadata, '$.source') = 'zooper_decomposition'
    ORDER BY timestamp DESC
    LIMIT 20
""")

for row in cursor:
    print(f"   '{row['content']}' (freq: {row['freq']})")

hf.close()
print("\n✅ Navigation complete!")
