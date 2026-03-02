#!/usr/bin/env python3
"""
Massive trigram generation - process many articles!
"""
import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm
import numpy as np
import json

print("🔤 MASSIVE TRIGRAM GENERATION 🔤")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
swarm = ZooperSwarm(hf, num_zooperlings=1)

# Count before
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'trigram'")
before_trigrams = cursor.fetchone()[0]
print(f"Trigram engrams before: {before_trigrams}")

# Process many articles
print("\nProcessing articles...")

cursor = hf.conn.execute(
    "SELECT id, content, coords_16d FROM engrams WHERE engram_type = 'knowledge' LIMIT 200"
)

articles = [(row['id'], row['content'], row['coords_16d']) for row in cursor]
print(f"Loaded {len(articles)} articles")

total_created = 0
for i, (article_id, content, coords_str) in enumerate(articles):
    coords = np.array(json.loads(coords_str))
    created = swarm._create_trigram_engrams(article_id, coords, content)
    total_created += len(created)
    
    if (i + 1) % 50 == 0:
        print(f"   Processed {i+1} articles, created {total_created} trigrams...")

# Show results
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'trigram'")
final_trigrams = cursor.fetchone()[0]

print(f"\n📊 Results:")
print(f"   Trigram engrams: {before_trigrams} → {final_trigrams} (+{final_trigrams - before_trigrams})")

# Show top trigrams by frequency
print(f"\n🔝 Top Trigrams by Frequency:")
cursor = hf.conn.execute(
    "SELECT content, metadata FROM engrams WHERE engram_type = 'trigram' ORDER BY json_extract(metadata, '$.frequency') DESC LIMIT 15"
)
for row in cursor:
    meta = json.loads(row['metadata'])
    freq = meta.get('frequency', 1)
    print(f"   '{row[0]}' (freq: {freq})")

hf.close()
print("\n✓ Massive trigram generation complete!")
