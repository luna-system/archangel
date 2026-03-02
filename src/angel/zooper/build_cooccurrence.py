#!/usr/bin/env python3
"""
Build Co-Occurrence Graph for Word-to-Word Navigation

Creates edges between words that appear in the same articles.
This enables proper Markov chain generation (word → word)!
"""

import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm
from collections import defaultdict
import numpy as np

print("🔗 BUILDING CO-OCCURRENCE GRAPH 🔗")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')

# Get all articles and their word engrams
print("\n📊 Loading article-word relationships...")

cursor = hf.conn.execute("""
    SELECT e.id as article_id, e.content as article_title
    FROM engrams e
    WHERE e.engram_type = 'knowledge'
    LIMIT 100  -- Start with sample
""")

articles = [(row['article_id'], row['article_title']) for row in cursor]
print(f"   Loaded {len(articles)} articles")

# For each article, get its words
co_occurrence = defaultdict(lambda: defaultdict(int))
word_freq = defaultdict(int)

print("\n🔄 Computing co-occurrences...")
for i, (article_id, title) in enumerate(articles):
    # Get all word engrams linked to this article
    cursor = hf.conn.execute("""
        SELECT target_id
        FROM engram_connections
        WHERE source_id = ? AND connection_type = 'HEBBIAN'
    """, (article_id,))
    
    word_ids = [row['target_id'] for row in cursor]
    
    # Get word contents
    word_contents = []
    for word_id in word_ids:
        cursor = hf.conn.execute(
            "SELECT content FROM engrams WHERE id = ? AND engram_type = 'language'",
            (word_id,)
        )
        row = cursor.fetchone()
        if row:
            word_contents.append(row['content'])
            word_freq[row['content']] += 1
    
    # Count co-occurrences within this article (all pairs)
    for i, w1 in enumerate(word_contents):
        for w2 in word_contents[i+1:]:
            if w1 != w2:
                co_occurrence[w1][w2] += 1
                co_occurrence[w2][w1] += 1
    
    if (i + 1) % 20 == 0:
        print(f"   Processed {i+1}/{len(articles)} articles...")

print(f"\n📈 Statistics:")
print(f"   Unique words with co-occurrences: {len(co_occurrence)}")
print(f"   Total co-occurrence pairs: {sum(len(v) for v in co_occurrence.values()) // 2}")

# Show top co-occurrences
print(f"\n🔝 Top Co-Occurring Word Pairs:")
sorted_pairs = []
for w1 in co_occurrence:
    for w2, count in co_occurrence[w1].items():
        if w1 < w2:  # Avoid duplicates
            sorted_pairs.append((w1, w2, count))

sorted_pairs.sort(key=lambda x: x[2], reverse=True)
for w1, w2, count in sorted_pairs[:20]:
    print(f"   '{w1}' ↔ '{w2}': {count} articles")

# Now create the edges!
print(f"\n💾 Creating CO_OCCUR edges...")

edge_count = 0
for w1 in co_occurrence:
    # Get w1's engram ID
    cursor = hf.conn.execute(
        "SELECT id FROM engrams WHERE content = ? AND engram_type = 'language'",
        (w1,)
    )
    row = cursor.fetchone()
    if not row:
        continue
    w1_id = row['id']
    
    for w2, count in co_occurrence[w1].items():
        # Get w2's engram ID
        cursor = hf.conn.execute(
            "SELECT id FROM engrams WHERE content = ? AND engram_type = 'language'",
            (w2,)
        )
        row = cursor.fetchone()
        if not row:
            continue
        w2_id = row['id']
        
        # Create CO_OCCUR edge (weight based on co-occurrence count)
        weight = min(0.5, 0.1 + count * 0.05)  # Max 0.5 weight
        
        cursor = hf.conn.execute("""
            INSERT OR REPLACE INTO engram_connections 
            (source_id, target_id, connection_type, weight, created_at, timestamp)
            VALUES (?, ?, 'CO_OCCUR', ?, datetime('now'), datetime('now'))
        """, (w1_id, w2_id, weight))
        
        edge_count += 1
        if edge_count % 100 == 0:
            print(f"   Created {edge_count} edges...")

hf.conn.commit()
print(f"\n✓ Created {edge_count} CO_OCCUR edges!")

# Verify
cursor = hf.conn.execute("SELECT COUNT(*) FROM engram_connections WHERE connection_type = 'CO_OCCUR'")
total_cooccur = cursor.fetchone()[0]
print(f"\n📊 Total CO_OCCUR edges in holofield: {total_cooccur}")

hf.close()
print("\n✓ Co-occurrence graph complete!")
