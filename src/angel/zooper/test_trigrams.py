#!/usr/bin/env python3
"""
Test trigram engram creation!
"""
import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm
import numpy as np
import json

print("🔤 TRIGRAM ENGRAM CREATION TEST 🔤")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
swarm = ZooperSwarm(hf, num_zooperlings=1)

# Count before
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'trigram'")
before_trigrams = cursor.fetchone()[0]
print(f"Trigram engrams before: {before_trigrams}")

# Process a few articles
print("\nProcessing articles for trigrams...")

test_articles = ["January", "February", "China", "Germany", "France"]
total_created = 0

for article_name in test_articles:
    cursor = hf.conn.execute(
        "SELECT id, content, coords_16d FROM engrams WHERE content LIKE ? AND engram_type = 'knowledge' LIMIT 1",
        (f"{article_name}%",)
    )
    row = cursor.fetchone()
    if not row:
        print(f"  {article_name}: Not found")
        continue
    
    article_id = row['id']
    content = row['content']
    coords = np.array(json.loads(row['coords_16d']))
    
    created = swarm._create_trigram_engrams(article_id, coords, content)
    total_created += len(created)
    
    if created:
        print(f"  {article_name}: Created {len(created)} trigram engrams")
        # Show what was created
        for tid in created:
            cursor = hf.conn.execute(
                "SELECT content FROM engrams WHERE id = ?",
                (tid,)
            )
            trow = cursor.fetchone()
            if trow:
                print(f"      '{trow['content']}'")

# Show results
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'trigram'")
final_trigrams = cursor.fetchone()[0]

print(f"\n📊 Results:")
print(f"   Trigram engrams: {before_trigrams} → {final_trigrams} (+{final_trigrams - before_trigrams})")

# Show sample trigrams
cursor = hf.conn.execute(
    "SELECT content, metadata FROM engrams WHERE engram_type = 'trigram' ORDER BY RANDOM() LIMIT 10"
)
print(f"\nSample trigram engrams:")
for row in cursor:
    meta = json.loads(row['metadata'])
    freq = meta.get('frequency', 1)
    print(f"   '{row[0]}' (freq: {freq})")

hf.close()
print("\n✓ Trigram test complete!")
