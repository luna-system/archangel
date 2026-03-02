#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager
from angel.zooper.triple_stream_generator import TripleStreamMarkovGenerator

print("🦊 TESTING IMPROVED GENERATION (1,060 words) 🦊")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
gen = TripleStreamMarkovGenerator(hf)

# Check available words
cursor = hf.conn.execute(
    "SELECT content FROM engrams WHERE engram_type = 'language' ORDER BY RANDOM() LIMIT 20"
)
available = [row[0] for row in cursor]
print(f"\nSample available words: {', '.join(available[:10])}")

# Test topical generation with more words now
print("\n" + "=" * 70)
print("TOPICAL GENERATION TESTS")
print("=" * 70)

topics = [
    (["january", "february", "march"], "Calendar"),
    (["france", "paris", "europe"], "Geography"),
    (["physics", "chemistry", "science"], "Science"),
    (["red", "blue", "green"], "Colors"),
    (["water", "ice", "snow"], "Water states"),
]

for words, name in topics:
    # Check which words exist
    existing = [w for w in words if gen._get_word(w)]
    if existing:
        print(f"\n📝 {name}: {', '.join(existing)}")
        text = gen.generate_topical(existing, length=20, temperature=0.8)
        print(f"   Generated: {text}")

# Compare stream personalities
print("\n" + "=" * 70)
print("STREAM COMPARISON (same start word)")
print("=" * 70)

if gen._get_word("time"):
    print("\n📝 Starting from 'time' (25 words each):")
    
    for name, weights in [
        ("Topical (PA-heavy)", (0.6, 0.2, 0.2)),
        ("Structural (SA-heavy)", (0.2, 0.6, 0.2)),
        ("Semantic (AA-heavy)", (0.2, 0.2, 0.6)),
        ("Balanced", (0.33, 0.33, 0.34)),
    ]:
        text = gen.generate("time", length=25, stream_weights=weights, temperature=0.9)
        print(f"\n   {name}:")
        print(f"   {text}")

# Stats
print("\n" + "=" * 70)
cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
word_count = cursor.fetchone()[0]
print(f"Total word engrams: {word_count}")

hf.close()
print("\n✓ Test complete!")
